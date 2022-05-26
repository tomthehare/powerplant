import Adafruit_DHT
from heat_index import calculate as heatindex
import time
import requests
import RPi.GPIO as GPIO
import logging
import signal
import sys
import os
import json
import datetime
from event_client import EventClient
import traceback
from task_coordinator import TaskCoordinator

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

event_client = EventClient()
task_coordinator = TaskCoordinator()

DHT_SENSOR = Adafruit_DHT.DHT22

PIN_TEMP_HUMIDITY_INSIDE = 18
PIN_TEMP_HUMIDITY_OUTSIDE = 15
PIN_FAN_POWER = 17
PIN_VALVE_1_POWER = 26
PIN_VALVE_2_POWER = 6
PIN_VALVE_3_POWER = 5
PIN_VALVE_4_POWER = -1
PIN_VALVE_5_POWER = -1
PIN_VALVE_6_POWER = -1
PIN_VALVE_7_POWER = 21
PIN_VALVE_8_POWER = 20
PIN_VALVE_9_POWER = 16

PIN_GROW_LIGHT_POWER = -1

SERVER_URL = 'http://192.168.86.182:5000'
URL_TEMP_HUMID_INSIDE = '/temp-humid-inside'
URL_TEMP_HUMID_OUTSIDE = '/temp-humid-outside'

FIVE_MINUTES = 300
TEN_MINUTES = 600
FIFTEEN_MINUTES = 900

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
        r = requests.post(url, data ={'data': data})

    def ask_if_plants_need_water(self, descriptor: str) -> bool:
        url = SERVER_URL + '/plant-thirst/' + descriptor
        response = requests.get(url)

        if response.status_code != 200:
            logging.error(str(response.status_code) + ' status code was received from ' + url)
            return False

        body = response.json()

        return body['thirsty']

    def read_valve_config(self):
        url = SERVER_URL + '/valve-config'
        r = requests.get(url)

        return r.json()

    def read_fan_config(self):
        url = SERVER_URL + '/fan-config'
        response = requests.get(url)

        return response.json()

    def read_watering_queue(self):
        url = SERVER_URL + '/valves/watering-queue'

        response = requests.get(url)
        return response.json()

    def post_event(self, payload):
        url = SERVER_URL +  '/events'

        response =  requests.post(url, data=payload)

        if response.status_code != 200:
            logging.error("Error posting event: %s" % response.json())

        return response.status_code == 200


class ValveConfig:

    def __init__(self, id):
        self.id = id
        self.description = ''
        self.conductivity_threshold = 1.0
        self.watering_delay_seconds = -1
        self.open_duration_seconds = -1


class Config:
    def __init__(self):
        self.valves = {}
        self.fan_temp = 85

    def update_fan_temp_config(self, fan_temp):
        if isinstance(fan_temp, dict):
            fan_temp = int(fan_temp['fan_temp'])

        self.fan_temp = int(fan_temp)

    def update_valve_config(self, input_config):
        for valve_config in input_config:
            valve_id = valve_config['valve_id']
            if valve_id not in self.valves.keys():
                self.valves[valve_id] = ValveConfig(valve_id)

            self.valves[valve_id].description = valve_config['description']
            self.valves[valve_id].conductivity_threshold = valve_config['conductivity_threshold']
            self.valves[valve_id].watering_delay_seconds = valve_config['watering_delay_seconds']
            self.valves[valve_id].open_duration_seconds = valve_config['open_duration_seconds']

        """
        example:

        {
            "valves":  [
                {
                    "id": 1,
                    "description": "LIMES",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 3600,
                    "open_duration_seconds": 30
                }
            ]
        }
        """

    def get_valve_config(self, valve_id):
        if valve_id not in self.valves.keys():
            raise Exception("Missing config for valve %d!" % valve_id)

        return self.valves[valve_id]


class ConfigSyncTask:
    def __init__(self, run_every_seconds, web_client: WebClient, config: Config):
        self.run_every_seconds = run_every_seconds
        self.last_run_ts = 0
        self.web_client = web_client
        self.config = config

    def should_run(self):
        return timestamp() > (self.last_run_ts + self.run_every_seconds)

    def run(self):
        if not self.should_run():
            return

        new_config = self.web_client.read_valve_config()
        logging.debug('Got new valve config: ' + json.dumps(new_config, indent=2))
        self.config.update_valve_config(new_config)

        new_fan_config = self.web_client.read_fan_config()
        logging.debug('Got new fan config: ' + json.dumps(new_fan_config, indent=2))
        self.config.update_fan_temp_config(new_fan_config)

        self.last_run_ts = timestamp()
        

class ValveLock:
    def __init__(self):
        self.locked_in_id = -1

    def acquire_lock(self, valve_id):
        valve_id = int(valve_id)

        if self.locked_in_id < 0:
            self.locked_in_id = valve_id
            return True
        
        return False

    def release_lock(self, valve_id):
        valve_id = int(valve_id)

        if self.locked_in_id == valve_id:
            self.locked_in_id = -1
            return True
        else:
            logger.warning('Valve %d not owning the lock asked for a release of the lock')
            return False

    def is_locked(self):
        return self.locked_in_id > 0

class TempHumidSensor:
    def __init__(self, pin):
        logging.info('Setting up temperature/humidity sensor on data pin %d', pin)
        self.data_pin = pin
        self.last_read_ts = 0

    def read(self):
        if (self.last_read_ts + 2) >= timestamp():
            msg = 'Too soon to read temp/humid on pin %d' % self.data_pin
            raise Exception(msg)

        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, self.data_pin)
        logging.debug('Read temp and humidity on pin %d: %f *F, %f percent Humidity', self.data_pin, temperature, humidity)
        self.last_read_ts = timestamp()

        if humidity is not None and temperature is not None:
            return TempHumidReading(temperature, humidity)
        else:
            logging.error('Unable to read temp/humidity on pin %d', self.data_pin)
            raise Exception('Unable to read sensor')

class FanTask:
    def __init__(self, run_every_seconds, power_pin, temp_humid_sensor: TempHumidSensor, config):
        self.temp_humid_sensor = temp_humid_sensor
        self.run_every_seconds = run_every_seconds
        self.power_pin = power_pin
        self.is_on = False
        self.last_run_ts = 0
        self.config = config

        logging.info('Setting up fan on pin %d', self.power_pin)

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

    def run(self):
        if timestamp() < (self.last_run_ts + self.run_every_seconds):
            return

        temp_now = self.temp_humid_sensor.read()
        temp_f_now = temp_now.get_temp()

        logging.debug('(fan) Current temp: ' + str(temp_f_now))
        logging.debug('(fan) Fan is: ' + ('on' if self.is_on else 'off'))

        if self.is_on and temp_f_now < self.config.fan_temp:
            self.turn_off()
        elif not self.is_on and temp_f_now > self.config.fan_temp:
            self.turn_on()            

        self.last_run_ts = timestamp()

    def turn_on(self):       
        GPIO.output(self.power_pin, GPIO.LOW)
        self.is_on = True
        event_client.log_fan_event(True)
        logging.info("Turned fan on")

    def turn_off(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.is_on = False
        event_client.log_fan_event(False)
        logging.info("Turned fan off")

    def shutdown(self):
        if self.is_on:
            self.turn_off()

class TempHumidLogTask:

    def __init__(self, run_every_seconds: int, sensor: TempHumidSensor, url: str, web_client: WebClient):
        self.run_every_seconds = run_every_seconds
        self.sensor = sensor
        self.last_run_ts = 0
        self.url = url
        self.web_client = web_client

    def should_run(self):
        should_run = timestamp() > (self.last_run_ts + self.run_every_seconds)
        #if not should_run:
            #logging.debug('Not ready for temp/humidity log task on pin %d', self.sensor.data_pin)
        return should_run

    def run(self) -> bool:
        if not self.should_run():
            return False

        reading = self.sensor.read()
        self.web_client.send_temp_humidity_reading(reading, self.url)
        self.last_run_ts = timestamp()

        return True

class Valve:
    def __init__(self, valve_id, signal_pin, valve_config):
        self.last_opened_time = 0
        self.id = valve_id
        self.is_open = False
        self.signal_pin = signal_pin
        self.valve_config = valve_config
        self.override_open_duration_seconds = -1
        logging.info('Setting up %s valve on pin %d', self.get_description(), self.signal_pin)

        GPIO.setup(self.signal_pin, GPIO.OUT)
        GPIO.output(self.signal_pin, GPIO.HIGH)

    def get_description(self):
        return self.valve_config.description

    def open(self, open_duration_seconds = -1):
        GPIO.output(self.signal_pin, GPIO.LOW)
        self.is_open = True
        self.last_opened_time = timestamp()
        if int(open_duration_seconds) > 0:
            self.override_open_duration_seconds = open_duration_seconds
 
        event_client.log_valve_event(self.id, True)
        logging.info('Valve for %s opened', self.get_description())

    def close(self):
        GPIO.output(self.signal_pin, GPIO.HIGH)
        self.is_open = False
        self.override_open_duration_seconds = -1
        event_client.log_valve_event(self.id, False)
        logging.info('Valve for %s closed', self.get_description())


class ValveCloseTask:
    def __init__(self, valve: Valve, valve_lock: ValveLock, config):
        self.valve = valve
        self.valve_lock = valve_lock
        self.config = config

    def run(self):
        #if int(self.valve.override_open_duration_seconds) < 0:
        #    closing_time = self.valve.last_opened_time + self.config.get_valve_config(self.valve.id).open_duration_seconds
        #else:
        #    closing_time = self.valve.last_opened_time + int(self.valve.override_open_duration_seconds)

        closing_time = self.valve.last_opened_time + self.config.get_valve_config(self.valve.id).open_duration_seconds

        if self.valve.is_open:
            logging.debug('Right now its %d, will close valve at %d', timestamp(), int(closing_time))

        if self.valve.is_open and timestamp() > int(closing_time):
            self.valve.close()
            self.valve_lock.release_lock(self.valve.id)
            return True

        return False

class WaterQueueTask:
    def __init__(self, web_client, run_every_seconds, valve_lock, valve_dict):
        self.web_client = web_client
        self.run_every_seconds = int(run_every_seconds)
        self.last_run_ts = 0
        self.valve_lock = valve_lock
        self.valve_dict = valve_dict

    def should_run(self):      
        return timestamp() > (self.last_run_ts + self.run_every_seconds)

    def run(self):
        if not self.should_run():
            return

        # If the valve is locked, just return without setting the time so it checks again soon
        if self.valve_lock.is_locked():
            return

        watering_queue = self.web_client.read_watering_queue()

        if not watering_queue:
            self.last_run_ts = timestamp()
            return

        # If the queue is > 1 entry, we should immediately jump into the next one, not wait
        if len(watering_queue) == 1:
            self.last_run_ts = timestamp()

        next_valve_id = watering_queue[0]['valve_id']
        open_duration_seconds = watering_queue[0]['valve_id']
        if self.valve_lock.acquire_lock(next_valve_id):
            url = SERVER_URL + '/valves/watering-queue/%s' % next_valve_id
            response = requests.delete(url)

            if response.status_code != 200:
                logging.error('Error received trying to dequeue valve')
                logging.error(response.json())
                return

            self.valve_dict[str(next_valve_id)].open(open_duration_seconds)

class WaterPlantTask:
    def __init__(self, run_every_seconds, valve: Valve, valve_lock: ValveLock):
        self.valve = valve
        self.valve_lock = va
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

        # Only water in the 9oclock hour once a day
        if current_hour() == 9 and (self.last_opened_timestamp() - timestamp()) > 86400:
            return True

        return False

    def run(self):
        if not self.should_run():
            return False
        
        self.valve.open()
        self.last_opened_timestamp = timestamp()
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

        logging.info("Light set to turn on at %d:%d and turn off at %d:%d" % (self.time_on_hour, self.time_on_minute, self.time_off_hour, self.time_off_minute))

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
        logging.info("turned off the grow lights")

    def turn_on_light(self):
        GPIO.output(self.power_pin, GPIO.LOW)
        self.light_on = True
        logging.info("turned on the grow lights")

    def run(self):
        if self.light_on and self.should_be_off():
            self.turn_off_light()
        elif not self.light_on and self.should_be_on():
            self.turn_on_light()

class EventSendingTask:
    def __init__(self, events_to_send, web_client):
        self.events_to_send = events_to_send
        self.web_client = web_client

    def run(self):
        counter = 0
        while counter < self.events_to_send:
            counter = counter + 1
            details = event_client.get_earliest_event()
            
            if not details:
                break

            filename = details['filename']
            payload = details['payload']

            if self.web_client.post_event(payload):
                event_client.delete_event(filename)
                logging.info('Sent Event: %s' % json.dumps(payload))

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    task_coordinator.shutdown()
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

config = Config()

config_sync_task = ConfigSyncTask(FIFTEEN_MINUTES, web_client, config)

# Grab initial settings for valves
config_sync_task.run()

valve_lock = ValveLock()
valve_1 = Valve(1, PIN_VALVE_1_POWER, config.get_valve_config(1))
valve_2 = Valve(2, PIN_VALVE_2_POWER, config.get_valve_config(2))
valve_3 = Valve(3, PIN_VALVE_3_POWER, config.get_valve_config(3))
valve_7 = Valve(7, PIN_VALVE_7_POWER, config.get_valve_config(7))
valve_8 = Valve(8, PIN_VALVE_8_POWER, config.get_valve_config(8))
valve_9 = Valve(9, PIN_VALVE_9_POWER, config.get_valve_config(9))

valve_dict = {'1': valve_1, '2': valve_2, '3': valve_3, '7': valve_7, '8': valve_8, '9': valve_9}

########################################
########### EXECUTE TASKS ##############
########################################

task_coordinator.register_task(config_sync_task)
task_coordinator.register_task(TempHumidLogTask(FIVE_MINUTES, tempHumidInside, SERVER_URL + URL_TEMP_HUMID_INSIDE, web_client))
task_coordinator.register_task(TempHumidLogTask(FIVE_MINUTES, tempHumidOutside, SERVER_URL + URL_TEMP_HUMID_OUTSIDE, web_client))
task_coordinator.register_task(FanTask(60, PIN_FAN_POWER, tempHumidInside, config))
task_coordinator.register_task(WaterQueueTask(web_client, 30, valve_lock, valve_dict))
task_coordinator.register_task(ValveCloseTask(valve_1, valve_lock, config))
task_coordinator.register_task(ValveCloseTask(valve_2, valve_lock, config))
task_coordinator.register_task(ValveCloseTask(valve_3, valve_lock, config))
task_coordinator.register_task(ValveCloseTask(valve_7, valve_lock, config))
task_coordinator.register_task(ValveCloseTask(valve_8, valve_lock, config))
task_coordinator.register_task(ValveCloseTask(valve_9, valve_lock, config))
task_coordinator.register_task(EventSendingTask(60, web_client))

task_coordinator.run()

GPIO.cleanup()

# End!
