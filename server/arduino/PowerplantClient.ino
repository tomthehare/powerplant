#include <stdint.h>
#include <stdlib.h>

/**
 * PIN ALLOCATIONS
 */
#define POWER_TO_SENSORS_SWITCH_PIN 13
#define SELECTPIN_A 2
#define SELECTPIN_B 3
#define SELECTPIN_C 4
#define SELECTPIN_D 5
#define MUX_ENABLE 7

void resetSoilMoisturePins() {
  digitalWrite(POWER_TO_SENSORS_SWITCH_PIN, HIGH); // High = off
  digitalWrite(SELECTPIN_A, LOW);
  digitalWrite(SELECTPIN_B, LOW);
  digitalWrite(SELECTPIN_C, LOW);
  digitalWrite(SELECTPIN_D, LOW);
  digitalWrite(MUX_ENABLE, HIGH);
}


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

class SoilMoistureSensor {
  private:
    int lastReadVoltage;
    OneShotScheduler *scheduler;
    int dataPin;
    long lastReadMillis;
    String tag;
    TimeCoordinator *tc;
    Logger *logger;

  /**
   * signalPins indicate which pins to activate to read the proper sensor.
   */
  public:
    SoilMoistureSensor(String tag, OneShotScheduler *scheduler, int dataPin, TimeCoordinator *tc, Logger *logger) {
      this->lastReadVoltage = -1;
      this->scheduler = scheduler;
      this->dataPin = dataPin;
      this->lastReadMillis = -1;
      this->tag = tag;
      this->tc = tc;
      this->logger = logger;
    }

    String readSensor() {
      if (!this->scheduler->shouldRunTask()) {
        return "";
      }

      this->scheduler->markTaskAsRun();

      digitalWrite(MUX_ENABLE, LOW);
      this->logger->doLog("MUX_ENABLE set to LOW");
      
      digitalWrite(POWER_TO_SENSORS_SWITCH_PIN, LOW);
      this->logger->doLog("POWER_TO_SENSORS_SWITCH_PIN set to LOW");

      // 0001
      if ((this->dataPin & 1) > 0) {
        digitalWrite(SELECTPIN_A, HIGH);
        this->logger->doLog("SEL0 set to HIGH");
      }

      // 0010
      if ((this->dataPin & 2) > 0) {
        digitalWrite(SELECTPIN_B, HIGH);
        this->logger->doLog("SEL1 set to HIGH"); 
      }

      // 0100
      if ((this->dataPin & 4) > 0) {
        digitalWrite(SELECTPIN_B, HIGH);
        this->logger->doLog("SEL2 set to HIGH"); 
      }

      // 1000
      if ((this->dataPin & 8) > 0) {
        digitalWrite(SELECTPIN_B, HIGH);
        this->logger->doLog("SEL3 set to HIGH"); 
      }

      delay(1000);

      this->lastReadVoltage = analogRead(A0);
      this->lastReadMillis = this->tc->getCurrentTimeStamp();
      
      this->resetSoilMoisturePins();

      String str = "&sm|";
      str.concat(this->tc->getCurrentTimeStamp());
      str.concat("|");
      str.concat(this->tag);
      str.concat("|");
      str.concat(this->lastReadVoltage);

      return str;
    }

    void resetSoilMoisturePins() {
      this->logger->doLog("Shutting down after read..");
      digitalWrite(POWER_TO_SENSORS_SWITCH_PIN, HIGH); // High = off
      this->logger->doLog("POWER_TO_SENSORS_SWITCH_PIN set to HIGH");
      digitalWrite(SELECTPIN_A, LOW);
      this->logger->doLog("SEL0 set to LOW");
      digitalWrite(SELECTPIN_B, LOW);
      this->logger->doLog("SEL1 set to LOW");
      digitalWrite(SELECTPIN_C, LOW);
      this->logger->doLog("SEL2 set to LOW");
      digitalWrite(SELECTPIN_D, LOW);
      this->logger->doLog("SEL3 set to LOW");
    }
};

SerialWriter serialWriter;
TimeCoordinator timeKeeper;
Logger logr(&serialWriter, &timeKeeper);

OneShotScheduler limeSensorScheduler0(15000);
SoilMoistureSensor limeSoilMoisureSensor0("lime-soil", &limeSensorScheduler0, 0, &timeKeeper, &logr);

OneShotScheduler limeSensorScheduler1(15000);
SoilMoistureSensor limeSoilMoisureSensor1("lime-air", &limeSensorScheduler1, 1, &timeKeeper, &logr);


void setup() { 
  Serial.begin(9600);

  pinMode(POWER_TO_SENSORS_SWITCH_PIN, OUTPUT);
  pinMode(SELECTPIN_A, OUTPUT);
  pinMode(SELECTPIN_B, OUTPUT);
  pinMode(SELECTPIN_C, OUTPUT);
  pinMode(SELECTPIN_D, OUTPUT);
  pinMode(MUX_ENABLE, OUTPUT);

  digitalWrite(POWER_TO_SENSORS_SWITCH_PIN, HIGH);
  digitalWrite(SELECTPIN_A, LOW);
  digitalWrite(SELECTPIN_B, LOW);
  digitalWrite(SELECTPIN_C, LOW);
  digitalWrite(SELECTPIN_D, LOW);
  digitalWrite(MUX_ENABLE, HIGH);

  // Solicit the real world time in order to schedule water delivery properly.
  timeKeeper.coordinateRealWorldTime();
  String logMessage = "Starting up... Arduino time synced: ";
  logMessage.concat(String(timeKeeper.getCurrentTimeStamp()));
  logr.doLog(logMessage);
}

void loop() {
  delay(3000);

  logr.doLog("Reading input sensor 0");
  String sensor0Reading = limeSoilMoisureSensor0.readSensor();

  if (sensor0Reading.length() > 0) {
    serialWriter.writeString(sensor0Reading); 
  }

  delay(3000);

  logr.doLog("Reading input sensor 1");
  String sensor1Reading = limeSoilMoisureSensor1.readSensor();

  if (sensor1Reading.length() > 0) {
    serialWriter.writeString(sensor1Reading); 
  }
}
