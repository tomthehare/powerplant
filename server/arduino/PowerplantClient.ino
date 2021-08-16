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

    long getCurrentTimeStamp() {
      return (millis() - this->arduinoStartTime) + this->realWorldStartTime;
    }
};

class Logger {
  private:
     SerialWriter *sw;
  
  public:
    Logger(SerialWriter *sw) {
      this->sw = sw;
    }

    void doLog(String aString) {
      String prefix = "log|";
      prefix.concat(aString);
      sw->writeString(prefix);
    }
};

class ValveOperator {
  private:
    TimeCoordinator *tc;
    Logger *logr;
    int secondsOpen;
 
  public:
    ValveOperator(Logger *logr, TimeCoordinator *tc, int secondsOpen) {
      this->secondsOpen = secondsOpen;
      this->logr = logr;
      this->tc = tc;
    }

    void evaluateSchedule() {
      return;
    }
};


SerialWriter serialWriter;
Logger logr(&serialWriter);
TimeCoordinator timeKeeper;
OneShotScheduler tempHumidScheduler(5000);
TempHumidityTask tempHumidity(&tempHumidScheduler);
ValveOperator mainWaterValve(&logr, &timeKeeper, 20);

void setup() {
  Serial.begin(9600);

  // Start(?) the temp/humdity chip
  dht.begin();

  // Solicit the real world time in order to schedule water delivery properly.
  timeKeeper.coordinateRealWorldTime();
}

void loop() {
  delay(5000);

  serialWriter.writeString("hello!");

  long currentTimestamp = timeKeeper.getCurrentTimeStamp();
  String currentTsString = String(currentTimestamp);
  logr.doLog(currentTsString);

//  serialWriter.writeString(tempHumidity.readSensor());
//  mainWaterValve.evaluateSchedule();
}
