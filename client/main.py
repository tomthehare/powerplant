import Adafruit_DHT
from heat_index import calculate as heatindex
import time
import requests
import RPi.GPIO as GPIO
import logging
import signal
import sys
import os
import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

DHT_SENSOR = Adafruit_DHT.DHT22

PIN_TEMP_HUMIDITY_INSIDE = 4
PIN_TEMP_HUMIDITY_OUTSIDE = -1 #TODO NUH UH change this to real pin
PIN_VALVE_POWER = 17
PIN_GROW_LIGHT_POWER = 14

SERVER_URL = 'http://192.168.86.182:5000'
URL_TEMP_HUMID_INSIDE = '/temp-humid-inside'
URL_TEMP_HUMID_OUTSIDE = '/temp-humid-outside'

def timestamp():
    return round(time.time())

def current_hour():
    return datetime.datetime.now().hour

def current_minute():
    return datetime.datetime.now().minute

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
    def format_temp_humidity_data_string(self, reading: TempHumidReading):
         return "&th|{timestamp}|humidity:{h}|temp:{t}|heat-index:{hi}".format(timestamp=timestamp(), h=reading.get_humidity(), t=reading.get_temp(), hi=reading.get_heat_index())

    def send_temp_humidity_reading(self, reading: TempHumidReading, url: str):
        data = self.format_temp_humidity_data_string(reading)
        logging.debug('sent web request: %s -> %s', url, data)
        #r = requests.post(url, data ={'data': data})

    def ask_if_plants_need_water(self, descriptor: str) -> bool:
        url = SERVER_URL + '/plant-thirst/' + descriptor
        response = requests.get(url)

        if response.status_code != 200:
            logging.error(str(response.status_code) + ' status code was received from ' + url)
            return False

        body = response.json()

        return body['thirsty']


class TempHumidSensor:

    def __init__(self, pin):
        logging.info('Setting up temperature/humidity sensor on data pin %d', pin)
        self.data_pin = pin
        self.last_read_ts = 0

    def read(self):
        if (self.last_read_ts + 2) >= timestamp():
            msg = 'Too soon to read temp/humid on pin %d' % self.data_pin
            logging.error(msg)
            raise Exception(msg)

        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, self.data_pin)
        logging.info('Read temp and humidity on pin %d: %f *F, %f percent Humidity', self.data_pin, temperature, humidity)
        self.last_read_ts = timestamp()

        if humidity is not None and temperature is not None:
            return TempHumidReading(temperature, humidity)
        else:
            logging.error('Unable to read temp/humidity on pin %d', self.data_pin)
            raise Exception('Unable to read sensor')

class TempHumidLogTask:

    def __init__(self, run_every_seconds: int, sensor: TempHumidSensor, url: str, web_client: WebClient):
        self.run_every_seconds = run_every_seconds
        self.sensor = sensor
        self.last_run_ts = 0
        self.url = url
        self.web_client = web_client

    def should_run(self):
        should_run = timestamp() > (self.last_run_ts + self.run_every_seconds)
        if not should_run:
            logging.debug('Not ready for temp/humidity log task on pin %d', self.sensor.data_pin)
        return should_run

    def run(self) -> bool:
        if not self.should_run():
            return False

        reading = self.sensor.read()
        self.web_client.send_temp_humidity_reading(reading, self.url)
        self.last_run_ts = timestamp()

        return True

class Valve:
    def __init__(self, signal_pin, open_duration, description: str):
        self.last_opened_time = 0
        self.open_duration = open_duration
        self.is_open = False
        self.signal_pin = signal_pin
        self.description = description
        logging.debug('Setting up valve on pin %d', self.signal_pin)

        GPIO.setup(self.signal_pin, GPIO.OUT)
        GPIO.output(self.signal_pin, GPIO.HIGH)

    def open(self):
        GPIO.output(self.signal_pin, GPIO.LOW)
        self.is_open = True
        self.last_opened_time = timestamp()
        logging.info('Valve on pin %d opened', self.signal_pin)

    def close(self):
        GPIO.output(self.signal_pin, GPIO.HIGH)
        self.is_open = False
        logging.info('Valve on pin %d closed', self.signal_pin)


class ValveCloseTask:
    def __init__(self, valve: Valve):
        self.valve = valve

    def run(self):
        if self.valve.is_open and timestamp() > (self.valve.last_opened_time + self.valve.open_duration):
            self.valve.close()
            return True

        return False

class WaterPlantTask:
    def __init__(self, run_every_seconds, valve: Valve, client: WebClient):
        self.valve = valve
        self.last_opened_timestamp = 0
        self.run_every_seconds = run_every_seconds
        self.last_evaluated_timestamp = 0
        self.client = client

    def should_run(self) -> bool:
        if timestamp() < (self.last_evaluated_timestamp + self.run_every_seconds):
            logging.debug('Plant %s not ready for evaluation yet', self.valve.description)
            return False

        self.last_evaluated_timestamp = timestamp()

        if self.valve.is_open:
            logging.debug('Valve %s already open', self.valve.description)
            return False

        if self.client.ask_if_plants_needs_water(self.valve.description):
            return True

        return False

    def run(self):
        if not self.should_run():
            return False
        
        self.valve.open()
        return True


class GrowLightTask:
    def __init__(self, time_on: str, time_off: str, power_pin: int):
        time_on_pieces = time_on.split(':')
        time_off_pieces = time_off.split(':')

        self.time_on_hour = int(time_on_pieces[0])
        self.time_on_minute = int(time_on_pieces[1])

        self.time_off_hour = int(time_off_pieces[0])
        self.time_off_minute = int(time_off_pieces[1])

        self.light_on = False
        self.power_pin = power_pin

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

        logging.debug("Light set to turn on at %d:%d and turn off at %d:%d" % (self.time_on_hour, self.time_on_minute, self.time_off_hour, self.time_off_minute))

    def should_be_on(self):
        turn_on_min_timestamp = (self.time_on_hour * 60) + self.time_on_minute
        turn_off_min_timestamp = (self.time_off_hour * 60) + self.time_off_minute
        now_min_timestamp = (current_hour() * 60) + current_minute()

        return turn_on_min_timestamp <= now_min_timestamp and now_min_timestamp < turn_off_min_timestamp

    def should_be_off(self):
        return not self.should_be_on()

    def turn_off_light(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.light_on = False
        logging.debug("turned off the grow lights")

    def turn_on_light(self):
        GPIO.output(self.power_pin, GPIO.LOW)
        self.light_on = True
        logging.debug("turned on the grow lights")

    def run(self):
        if self.light_on and self.should_be_off():
            self.turn_off_light()
        elif not self.light_on and self.should_be_on():
            self.turn_on_light()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    GPIO.cleanup()
    sys.exit(0)

########################################
################# SET UP ###############
########################################

logging.info('Starting up...')
signal.signal(signal.SIGINT, signal_handler)

# use the numbers printed on the guides, not the ones on the board
GPIO.setmode(GPIO.BCM)

tempHumidInside = TempHumidSensor(PIN_TEMP_HUMIDITY_INSIDE)
tempHumidOutside = TempHumidSensor(PIN_TEMP_HUMIDITY_OUTSIDE)
web_client = WebClient()
valve = Valve(PIN_VALVE_POWER, 30, 'LimeTree')
########################################
########### EXECUTE TASKS ##############
########################################

tasks = [
    #TempHumidLogTask(10, tempHumidInside, SERVER_URL + URL_TEMP_HUMID_INSIDE, web_client),
    #TempHumidLogTask(15, tempHumidOutside, SERVER_URL + URL_TEMP_HUMID_OUTSIDE, web_client),
    #WaterPlantTask(300, valve, web_client),
    #ValveCloseTask(valve),
    GrowLightTask('05:00', '19:00', PIN_GROW_LIGHT_POWER),
]

while True:
    for task in tasks:
        try:
            task.run();
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error(e)
            print(exc_type, fname, exc_tb.tb_lineno) 


    time.sleep(5);

GPIO.cleanup()
