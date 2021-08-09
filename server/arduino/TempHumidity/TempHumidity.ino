#include <Adafruit_Sensor.h>

#include <stdint.h>
#include <DHT.h>
#include <DHT_U.h>

#include <Adafruit_Sensor.h>


#define DHTPIN 2     // what digital pin we're connected to
  
// Uncomment whatever type you're using!
//#define DHTTYPE DHT11   // DHT 11
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
//#define DHTTYPE DHT21   // DHT 21 (AM2301)

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);

  dht.begin();
}

void loop() {
  // Wait a few seconds between measurements.
  delay(30000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();

  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(f)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(f, h);

  Serial.print("humidity:");
  Serial.print(h);
  Serial.print("|");
  Serial.print("temp-fht:");
  Serial.print(f);
  Serial.print("|");
  Serial.print("heat-index-fht:");
  Serial.print(hif);
  Serial.println("");
}
