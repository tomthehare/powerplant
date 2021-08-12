#include <Adafruit_Sensor.h>
#include <stdint.h>
#include <DHT.h>
#include <DHT_U.h>

#include <Adafruit_Sensor.h>


#define DHTPIN 2     // what digital pin we're connected to
  
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);

  dht.begin();
}

class SyncTimerTask {
  
};

class TempHumidityTask {
  long ReadEveryMillis;
  long LastReadMillis;

  public:
  TempHumidityTask(long readEveryMillis) {
    ReadEveryMillis = readEveryMillis;
    LastReadMillis = millis();
  }

  String readSensor() {
    String debugPrinter = String(LastReadMillis);
    debugPrinter.concat("|");
    debugPrinter.concat(String(millis()));
    Serial.print(debugPrinter);
    
    if (!shouldRunTask()) {
      return "";
    }

    LastReadMillis = millis();

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

    String str = "&th|humidity:";
    str.concat(h);
    str.concat("|");
    str.concat("temp-fht:");
    str.concat(f);
    str.concat("|");
    str.concat("heat-index-fht:");
    str.concat(hif);
    str.concat('\n');

    return str;
  } 
  
  bool shouldRunTask() {
    return millis() >= (LastReadMillis + ReadEveryMillis);
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
    
    int bytesWritten = Serial.print(string); 

    return bytesWritten > 0;
  }
};

SerialWriter serialWriter();
TempHumidityTask tempHumidity(5000);

void loop() {
  delay(1000);
  Serial.println("hello");
  //String tmpHumidReading = tempHumidity.readSensor();

  //if (tmpHumidReading != "") {
  //  Serial.print(tmpHumidReading);
  //}
}
