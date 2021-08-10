#include <Adafruit_Sensor.h>
#include <string>
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
  
}

class TempHumidityTask {
  long ReadEveryMillis;
  long LastReadMillis;

  public:
  TempHumidityTask(long readEveryMillis) {
    ReadEveryMillis = readEveryMillis;
    LastReadMillis = millis();
  }

  std::string readSensor() {
    if (!shouldRunTask()) {
      return "";
    }

    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    float h = dht.readHumidity();
 
    // Read temperature as Fahrenheit (isFahrenheit = true)
    float f = dht.readTemperature(true);

    // Check if any reads failed and exit early (to try again).
    if (isnan(h) || isnan(f)) {
      Serial.println;
      return "Failed to read from DHT sensor!";
    }

    // Compute heat index in Fahrenheit (the default)
    float hif = dht.computeHeatIndex(f, h);

    std::string str = "&th|humidity:";
    str.append(h);
    str.append("|");
    str.append("temp-fht:");
    str.append(f);
    str.append("|");
    str.append("heat-index-fht:");
    str.append(hif);
    str.append('\n');

    return str;
  }
  
  bool shouldRunTask() {
    return millis() >= (LastReadMillis + ReadEveryMillis);
  }

}

TempHumidityTask tempHumidity(60000);

void loop() {
  std::string tmpHumidReading = tempHumidity.read();

  if (tmpHumidReading != "") {
    Serial.print(tmpHumidReading);
  }
}
