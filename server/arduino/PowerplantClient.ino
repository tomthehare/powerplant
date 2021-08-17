#include <Adafruit_Sensor.h>
#include <stdint.h>
#include <DHT.h>
#include <DHT_U.h>
#include <stdlib.h>

#include <Adafruit_Sensor.h>


#define DHTPIN 2     // what digital pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321

DHT dht(DHTPIN, DHTTYPE);


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

class TempHumidityTask {
  private:
    OneShotScheduler *scheduler;

  public:
    TempHumidityTask(OneShotScheduler *scheduler) {
      this->scheduler = scheduler;
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
  
      // Check if any reads failed and exit early (to try again).
      if (isnan(h) || isnan(f)) {
        return "&err|Failed to read temp-humid sensor.";
      }
  
      // Compute heat index in Fahrenheit (the default)
      float hif = dht.computeHeatIndex(f, h);

      this->scheduler->markTaskAsRun();
  
      String str = "&th|humidity:";
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

class TimeCoordinator {
  private:
    long realWorldStartTime;
    long arduinoStartTime;
    bool realWorldTimeSynced;

  public:
    TimeCoordinator() {
      this->arduinoStartTime = millis();
      this->realWorldStartTime = 0;
      this->realWorldTimeSynced = false;;
    }

    /**
     * Mzking the assumption that we are getting the unix time stamp which is offset for EST already.
     */
    void coordinateRealWorldTime() {
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
    }

    /**
     * Get Current timestamp - note it's already in EST (or we are assuming that)
     */
    long getCurrentTimeStamp() {
      return (millis() - this->arduinoStartTime) + this->realWorldStartTime;
    }

    /**
     * Get the integer of the hour that it is.
     */
    int getCurrentHourOffset() {
      int daySeconds = this.getCurrentTimestamp() % 86400;

      // Integer division should floor this to whateve the hour is, I think.
      return daySeconds / 3600;
    }

    /**
     * Get current day offset from epoch
     */
    int getDayOffset() {
      return this.getCurrentTimestamp() / 86400;
    }
};

class Logger {
  private:
     SerialWriter *sw;
     TimeCoordinator tc;
  
  public:
    Logger(SerialWriter *sw, TimeCoordinator *tc) {
      this->sw = sw;
      this->tc = tc;
    }

    void doLog(String aString) {
      String prefix = "log|"
      prefix.concat(this->tc->getCurrentTimestamp());
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
    int lastDayOffsetRun;
    long valveOpenedAtTimestamp;
    bool valveOpen;
 
  public:
    ValveOperator(Logger *logr, TimeCoordinator *tc, int secondsOpen, OneShotScheduler *scheduler) {
      this->secondsOpen = secondsOpen;
      this->logr = logr;
      this->tc = tc;
      this->scheduler = scheduler;
      this->lastDayOffsetRun = 0;
    }

    void evaluateSchedule() {
      if (!this->scheduler->shouldRunTask()) {
        return;
      }

      this->scheduler->markTaskAsRun();

      if (this->valveOpen) {
        if (this->tc->getCurrrentTimeOffset() > (this->valveOpenedAtTimestamp + this->secondsOpen)) {
          this->lastDayOffsetRun = this->tc->getDayOffset();
          this.closeValve();
        } else {
          // The valve is open and doesnt need to be closed yet.  We can evaluate again soon.
          return;
        }
      }

      // Do the 8am check
      if (this->tc->getDayOffset() != this->lastDayOffsetRun && this->tc->getCurrentHourOffset() == 8) {
        this.openValve();
      }
    }

    void openValve() {
      // GIVE POWER TO PIN
      this->valveOpen = true;
      this->valveOpenedAtTimestamp = this->tc->getCurrentTimestamp();
    }

    void closeValve() {
      // TAKE POWER AWAY
      this->valveOpen = false;
      this->valveOpenedAtTimestamp = 0;
    }
};


SerialWriter serialWriter;
TimeCoordinator timeKeeper;
Logger logr(&serialWriter, &timeKeeper);
OneShotScheduler tempHumidScheduler(5000);
TempHumidityTask tempHumidity(&tempHumidScheduler);
OneShotScheduler mainWaterValveScheduler(5000);
ValveOperator mainWaterValve(&logr, &timeKeeper, 20, &mainWaterValveScheduler);

void setup() {
  Serial.begin(9600);

  // Start(?) the temp/humdity chip
  dht.begin();

  // Solicit the real world time in order to schedule water delivery properly.
  timeKeeper.coordinateRealWorldTime();
}

void loop() {
  delay(5000);

  logr.doLog("checking in");

//  serialWriter.writeString(tempHumidity.readSensor());
//  mainWaterValve.evaluateSchedule();
}
