#include <Adafruit_Sensor.h>
#include <stdint.h>
#include <DHT.h>
#include <DHT_U.h>
#include <stdlib.h>

#include <Adafruit_Sensor.h>


#define DHTPIN 2     // what digital pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321

DHT dht(DHTPIN, DHTTYPE);

#define PIN_WATERVALVE 7
#define VALVE_COOLDOWN_SECONDS 60

class OneShotScheduler {
  private:
    long readEveryMillis;
    long lastReadMillis;
  
  public:
    OneShotScheduler(long everyMillis) {
        this->readEveryMillis = everyMillis;
        this->lastReadMillis = millis();
    }

    bool shouldRunTask() {
      return millis() >= (this->lastReadMillis + this->readEveryMillis);
    }

    void markTaskAsRun() {
      this->lastReadMillis = millis();
    }
};

class TimeCoordinator {
  private:
    long realWorldStartTime;
    long arduinoStartTime;
    bool realWorldTimeSynced;

  public:
    TimeCoordinator() {
      this->arduinoStartTime = millis();
      this->realWorldStartTime = 0;
      this->realWorldTimeSynced = false;
    }

    /**
     * Mzking the assumption that we are getting the unix time stamp which is offset for EST already.
     */
    void coordinateRealWorldTime() {
      if (this->realWorldTimeSynced == true) {
        return;
      }
      
      String timeString;
      Serial.println("time-please");
      while (true) {
        if (Serial.available()) {
          timeString = Serial.readStringUntil('>');
          break;
        } else {
          delay(1000);
        }
      }

      this->realWorldStartTime = timeString.toInt();
      this->realWorldTimeSynced = true;
    }

    /**
     * Get Current timestamp - note it's already in EST (or we are assuming that)
     */
    long getCurrentTimeStamp() {
      return ((millis() / 1000) - this->arduinoStartTime) + this->realWorldStartTime;
    }

    /**
     * Get the integer of the hour that it is.
     */
    int getCurrentHourOffset() {
      long daySeconds = this->getCurrentTimeStamp() % 86400;

      // Integer division should floor this to whateve the hour is, I think.
      return daySeconds / 3600;
    }

    int getCurrentMinuteOffset() {
      long daySeconds = this->getCurrentTimeStamp() % 86400;

      int hourSeconds = daySeconds % 3600;

      return hourSeconds / 60;
    }

    /**
     * Get current day offset from epoch
     */
    int getCurrentDayOffset() {
      return this->getCurrentTimeStamp() / 86400;
    }
};

class TempHumidityTask {
  private:
    OneShotScheduler *scheduler;
    TimeCoordinator *tc;
    float lastTempReading;

  public:
    TempHumidityTask(OneShotScheduler *scheduler, TimeCoordinator *tc) {
      this->scheduler = scheduler;
      this->tc = tc;
    }
  
    float getLastTempReading() {
      return this->lastTempReading;
    }

    String readSensor() {    
      if (!this->scheduler->shouldRunTask()) {
        return "";
      }
    
      // Reading temperature or humidity takes about 250 milliseconds!
      // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
      float h = dht.readHumidity();
   
      // Read temperature as Fahrenheit (isFahrenheit = true)
      float f = dht.readTemperature(true);
      this->lastTempReading = f;
  
      // Check if any reads failed and exit early (to try again).
      if (isnan(h) || isnan(f)) {
        return "&err|Failed to read temp-humid sensor.";
      }
  
      // Compute heat index in Fahrenheit (the default)
      float hif = dht.computeHeatIndex(f, h);

      this->scheduler->markTaskAsRun();
  
      String str = "&th|";
      str.concat(this->tc->getCurrentTimeStamp());
      str.concat("|humidity:");
      str.concat(h);
      str.concat("|");
      str.concat("temp-fht:");
      str.concat(f);
      str.concat("|");
      str.concat("heat-index-fht:");
      str.concat(hif);
  
      return str;
    }
};

class SerialWriter {

  public:
    SerialWriter() {}

    bool writeString(String string) {
      // No need to write nothing - this is going to be treated as success.
      if (string.equals("")) {
        return true;
      }
    
      int bytesWritten = Serial.println(string); 

      return bytesWritten > 0;
    }
};

class Logger {
  private:
     SerialWriter *sw;
     TimeCoordinator *tc;
  
  public:
    Logger(SerialWriter *sw, TimeCoordinator *tc) {
      this->sw = sw;
      this->tc = tc;
    }

    void doLog(String aString) {
      String prefix = "&log|";
      prefix.concat(this->tc->getCurrentTimeStamp());
      prefix.concat("|");
      prefix.concat(aString);
      sw->writeString(prefix);
    }
};

class ValveOperator {
  private:
    TimeCoordinator *tc;
    Logger *logr;
    int secondsOpen;
    OneShotScheduler *scheduler;
    int lastDayOffsetRun8;
    int lastDayOffsetRun12;
    long valveOpenedAtTimestamp;
    bool valveOpen;
    TempHumidityTask *tempHumid;
 
  public:
    ValveOperator(Logger *logr, TimeCoordinator *tc, int secondsOpen, OneShotScheduler *scheduler, TempHumidityTask *tempHumid) {
      this->secondsOpen = secondsOpen;
      this->logr = logr;
      this->tc = tc;
      this->scheduler = scheduler;
      this->lastDayOffsetRun8 = 0;
      this->lastDayOffsetRun12 = 0;
      this->tempHumid = tempHumid;
    }

    void evaluateSchedule() {
      if (!this->scheduler->shouldRunTask()) {
        return;
      }

      this->scheduler->markTaskAsRun();

      if (this->valveOpen) {
        if (this->tc->getCurrentTimeStamp() > (this->valveOpenedAtTimestamp + this->secondsOpen)) {
          this->closeValve();
        } else {
          // The valve is open and doesnt need to be closed yet.  We can evaluate again soon.
          return;
        }
      }

      int currentDay = this->tc->getCurrentDayOffset();
      int currentHour = this->tc->getCurrentHourOffset();
      int currentMinute = this->tc->getCurrentMinuteOffset();

      // Do the 8am check
      if (currentDay != this->lastDayOffsetRun8 && this->tc->getCurrentHourOffset() == 8) {
        this->openValve();
	this->lastDayOffsetRun8 = this->tc->getCurrentDayOffset();
      }

      if (currentDay != this->lastDayOffsetRun12 && this->tc->getCurrentHourOffset() == 12 && this->tempHumid->getLastTempReading() > 100) {
        this->openValve();
	String logString = "Did the 12pm check and determined that it is plenty hot: ";
        logString.concat(this->tempHumid->getLastTempReading());
	this->logr->doLog(logString);
        this->lastDayOffsetRun12 = this->tc->getCurrentDayOffset();
      } else {
        String logString = "Did the 12pm check but determined not hot enough today: ";
        logString.concat(this->tempHumid->getLastTempReading());
	this->logr->doLog(logString);
      }
    }

    void openValve() {
      digitalWrite(PIN_WATERVALVE, HIGH);
      this->valveOpen = true;
      this->valveOpenedAtTimestamp = this->tc->getCurrentTimeStamp();
      
      this->logr->doLog("Opened valve");
    }

    void closeValve() {
      digitalWrite(PIN_WATERVALVE, LOW);
      this->valveOpen = false;
      this->valveOpenedAtTimestamp = 0;
      this->logr->doLog("Closed valve");
    }
};


SerialWriter serialWriter;
TimeCoordinator timeKeeper;
Logger logr(&serialWriter, &timeKeeper);
OneShotScheduler tempHumidScheduler(60000);
TempHumidityTask tempHumidity(&tempHumidScheduler, &timeKeeper);
OneShotScheduler mainWaterValveScheduler(10000); // evaluate if it should run every n milliseconds, this does not mean it will run, just that it will have a chance to evaluate.
ValveOperator mainWaterValve(&logr, &timeKeeper, 30, &mainWaterValveScheduler, &tempHumidity);

void setup() {
  Serial.begin(9600);

  pinMode(PIN_WATERVALVE, OUTPUT); 

  // Start(?) the temp/humdity chip
  dht.begin();

  // Solicit the real world time in order to schedule water delivery properly.
  timeKeeper.coordinateRealWorldTime();
  String logMessage = "Arduino time synced: ";
  logMessage.concat(String(timeKeeper.getCurrentTimeStamp()));
  logr.doLog(logMessage);
}

void loop() {
  delay(100);

  String tempHumid = tempHumidity.readSensor();

  if (tempHumid.length() > 0) {
    serialWriter.writeString(tempHumid);
  }
  
  mainWaterValve.evaluateSchedule();
}