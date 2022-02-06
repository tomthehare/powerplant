import Adafruit_DHT
from heat_index import calculate as heatindex
import time
import requests
import RPi.GPIO as GPIO

# TODO ID LIKE SOME LOGGING

DHT_SENSOR = Adafruit_DHT.DHT22

PIN_TEMP_HUMIDITY_INSIDE = 4
PIN_TEMP_HUMIDITY_OUTSIDE = 4 #TODO NUH UH change this to real pin
PIN_VALVE_POWER = -1
PIN_SOIL_MOISTURE_POWER = -1
PIN_SOIL_MOISTURE_DATA = -1

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
         return "not_relevant|{timestamp}|humidity:{h}|temp:{t}|heat-index:{hi}".format(timestamp=timestamp(), h=reading.get_humidity(), t=reading.get_temp(), hi=reading.get_heat_index())

    def send_temp_humidity_reading(self, reading: TempHumidReading, url: str):
        data = self.format_data_string(reading)
        print(data)
        r = requests.post(url, data ={'data': data})

class SoilMoistureSensor:
    def __init__(self, data_pin, power_pin):
        self.data_pin = data_pin
        self.power_pin = power_pin
        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.setup(self.data_pin, GPIO.IN)

    def read(self) -> float:
        # No idea, will return a value though
        # givee it power
        # wait a bit
        # take data reading
        # turn off the power

        return .9 #total guess at a high number

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

    def __init__(self, run_every_seconds: int, sensor: TempHumidSensor, url: str, web_client: WebClient):
        self.run_every_seconds = run_every_seconds
        self.sensor = sensor
        self.last_run_ts = 0
        self.url = url
        self.web_client = web_client

    def should_run(self):
        return timestamp() > (self.last_run_ts + self.run_every_seconds)

    def run(self) -> bool:
        if not self.should_run():
            print('task not ready yet')
            return False

        reading = self.sensor.read()
        self.web_client.send_temp_humidity_reading(reading, self.url)
        self.last_run_ts = timestamp()

        return True

class Valve:
    def __init__(self, signal_pin, open_duration):
        self.last_opened_time = 0
        self.open_duration = open_duration
        self.is_open = False
        self.signal_pin = signal_pin

        GPIO.setup(self.signal_pin, GPIO.OUT)

    def open(self):
        GPIO.output(self.signal_pin, GPIO.HIGH)
        self.is_open = True
        self.last_opened_time = timestamp()

    def close(self):
        GPIO.output(self.signal_pin, GPIO.LOW)
        self.is_open = False

class ValveCloseTask:
    def __init__(self, valve: Valve):
        self.valve = valve

    def run(self):
        if self.valve.is_open and timestamp() > (self.valve.last_opened_time + self.valve.open_duration):
            self.valve.close()
            return True

        return False

class WaterPlantTask:
    def __init__(self, run_every_seconds, valve: Valve, soil_moisture_sensor: SoilMoistureSensor, soil_moisture_threshold: float):
        self.valve = valve
        self.soil_moisture_sensor = soil_moisture_sensor
        self.last_opened_timestamp = 0
        self.soil_moisture_threshold = soil_moisture_threshold
        self.cooldown_seconds = 300
        self.run_every_seconds = run_every_seconds
        self.last_evaluated_timestamp = 0

    def should_run(self) -> bool:
        if timestamp() < (this.last_evaluated_timestamp + self.run_every_seconds):
            return False

        self.last_evaluated_timestamp = timestamp()

        soil_moisture_reading = self.soil_moisture_sensor.read()
        if soil_moisture_reading < this.soild_moisture_threshold:
            if (self.last_opened_timestamp + self.cooldown_seconds) < timestamp():
                return True

        return False

    def run(self):
        if not self.should_run():
            return False
        
        self.valve.open()
        return True

# use board numbers vs some lower level option
GPIO.setmode(GPIO.BOARD)

tempHumidInside = TempHumidSensor(PIN_TEMP_HUMIDITY_INSIDE)
tempHumidOutside = TempHumidSensor(PIN_TEMP_HUMIDITY_OUTSIDE)
web_client = WebClient()
soil_moisture_sensor = SoilMoistureSensor(PIN_SOIL_MOISTURE_DATA, PIN_SOIL_MOISURE_POWER)
valve = Valve(PIN_VALVE_POWER, 30)

tasks = [
    TempHumidLogTask(10, tempHumidInside, SERVER_URL + URL_TEMP_HUMID_INSIDE, web_client), 
    TempHumidLogTask(15, tempHumidOutside, SERVER_URL + URL_TEMP_HUMID_OUTSIDE, web_client),
    WaterPlantTask(600, valve, soil_moisture_sensor, .8),
]

while True:
    for task in tasks:
        try:
            task.run();
        except Exception as e:
            print(e)
    
    time.sleep(5);
