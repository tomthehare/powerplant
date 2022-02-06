import Adafruit_DHT
from heat_index import calculate as heatindex
import time
import requests

DHT_SENSOR = Adafruit_DHT.DHT22

PIN_TEMP_HUMIDITY_INSIDE = 4
PIN_TEMP_HUMIDITY_OUTSIDE = -1

SERVER_URL = 'http://192.168.86.182:5000'
URL_TEMP_HUMID_INSIDE = '/temp-humid-inside'
URL_TEMP_HUMID_OUTSIDE = '/temp-humid-outside'

def timestamp():
    return round(time.time())

class TempHumidReading:
    def __init__(self, temp, humid):
        self.temp_c = temp
        self.humid = humid

    def get_temp(self):
        return round((9 * self.temp_c) / 5 + 32, 1)

    def get_temperature(self):
        return self.get_temp()

    def get_humidity(self):
        return round(self.humid, 1)

    def get_heat_index(self):
        return round(heatindex.from_fahrenheit(self.get_temp(), self.get_humidity()), 1)

class WebClient:

    def format_data_string(self, reading: TempHumidReading):
         data = "th_inside|{timestamp}|humidity:{h}|temp:{t}|heat-index:{hi}".format(timestamp=timestamp(), h=reading.get_humidity(), t=reading.get_temp(), hi=reading.get_heat_index())

    def send_temp_humidity_reading(self, reading: TempHumidReading, url: str):
        #r = requests.post(url, data ={'data': self.format_data_string(reading)})

        print(data)
        #r = requests.post(SERVER_URL + '/temp-humid-inside', data ={'data': data})

class TempHumidSensor:

    def __init__(self, pin):
        self.data_pin = pin
        self.last_read_ts = 0

    def read(self):
        if (self.last_read_ts + 2) >= timestamp():
            raise Exception('Too soon to read temp/humid')

        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, self.data_pin)
        self.last_read_ts = timestamp()

        if humidity is not None and temperature is not None:
            return TempHumidReading(temperature, humidity)
        else:
            raise Exception('Unable to read sensor')

class TempHumidLogTask:

    def __init__(self, run_every_seconds: int, sensor: TempHumiditySensor, url: str, web_client: WebClient):
        self.run_every_seconds = run_every_seconds
        self.sensor = sensor
        self.last_run_ts = 0
        self.url = url
        self.web_client = web_client

    def should_run(self):
        return timestamp() > (self.last_run_ts + self.run_every_seconds)

    def run(self) -> bool:
        if not self.should_run():
            return False

        reading = self.sensor.read()
        self.web_client.send_temp_humidity_reading(reading, self.url)
        self.last_run_ts = timestamp()

        return True


tempHumidInside = TempHumidSensor(PIN_TEMP_HUMIDITY_INSIDE)
tempHumidOutside = TempHumidSensor(PIN_TEMP_HUMIDITY_OUTSIDE)
web_client = WebClient()

tasks = [
    TempHumidLogTask(300, tempHumidInside, SERVER_URL + URL_TEMP_HUMIDITY_INSIDE, web_client), 
    TempHumidLogTask(300, tempHumidOutside, SERVER_URL + URL_TEMP_HUMIDITY_OUTSIDE, web_client),
]
