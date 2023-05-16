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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

event_client = EventClient()
task_coordinator = TaskCoordinator()

DHT_SENSOR = Adafruit_DHT.DHT22

PIN_TEMP_HUMIDITY_INSIDE = 21
PIN_TEMP_HUMIDITY_OUTSIDE = 20
PIN_FAN_POWER = 27
PIN_PUMP_POWER = 17
PIN_VALVE_1_POWER = 2
PIN_VALVE_2_POWER = 3
PIN_VALVE_3_POWER = 14
PIN_VALVE_4_POWER = 4
PIN_VALVE_5_POWER = 15
PIN_VALVE_6_POWER = 18
PIN_VALVE_7_POWER = 23
PIN_VALVE_8_POWER = 24
PIN_VALVE_9_POWER = 1
PIN_CIRC_FAN_POWER = 22
PIN_WINDOW_SE_INPUT_A = 25
PIN_WINDOW_SE_INPUT_B = 8

PIN_GROW_LIGHT_POWER = -1

VALVE_CLEAR_SLEEP_SECONDS = 2

SERVER_URL = 'http://192.168.86.172:5000'
URL_TEMP_HUMID_INSIDE = '/temp-humid-inside'
URL_TEMP_HUMID_OUTSIDE = '/temp-humid-outside'

FIVE_MINUTES = 300
TEN_MINUTES = 600
FIFTEEN_MINUTES = 900

def timestamp():
    return round(time.time())

def current_day():
    return datetime.date.today().timetuple().tm_yday

def current_hour():
    return datetime.datetime.now().hour

def current_minute():
    return datetime.datetime.now().minute


class TempHumidReading:
    def __init__(self, temp, humid):
        self.temp_c = temp
        self.humid = humid
        self.read_at_ts = timestamp()

    def get_temp(self):
        return round((9 * self.temp_c) / 5 + 32, 1)

    def get_temperature(self):
        return self.get_temp()

    def get_humidity(self):
        return round(self.humid, 1)

    def get_heat_index(self):
        return round(heatindex.from_fahrenheit(self.get_temp(), self.get_humidity()), 1)
    
    def to_string(self):
        return json.dumps({'temperature': self.get_temperature(), 'humidity': self.get_humidity()}, indent=2)
        

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

    def water_all(self):
        url = SERVER_URL + '/valves/water'

        response = requests.post(url)
        
        return response.status_code == 200

    def dequeue_valve(self, valve_id):
        url = SERVER_URL + '/valves/watering-queue/%s' % valve_id
        response = requests.delete(url)

        if response.status_code != 200:
            logging.error('Error received trying to dequeue valve')
            logging.error(response.json())
            return False

        return True


class ValveConfig:
    def __init__(self, id):
        self.id = id
        self.description = 'UNKNOWN'
        self.conductivity_threshold = 1.0
        self.watering_delay_seconds = 1
        self.open_duration_seconds = 1

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
            return ValveConfig(valve_id)

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
        self.last_reading = None

    def read(self):
        if (self.last_read_ts + 2) >= timestamp():
            logging.info('Too soon to read temp/humid on pin %d' % self.data_pin)
            return
        
        self.last_read_ts = timestamp()

        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, self.data_pin)
        logging.debug('Read temp and humidity on pin %d: %f *F, %f percent Humidity', self.data_pin, temperature, humidity)

        if humidity is not None and temperature is not None:
            self.last_reading = TempHumidReading(temperature, humidity)
            return self.last_reading
        else:
            logging.error('Unable to read temp/humidity on pin %d', self.data_pin)
            raise Exception('Unable to read sensor')

    def get_last_reading(self):
        return self.last_reading

class CirculatorFansTask:
    def __init__(self, run_every_seconds, power_pin, on_every_seconds, run_duration_seconds):
        self.run_every_seconds = run_every_seconds
        self.power_pin = power_pin
        self.on_every_seconds = on_every_seconds
        self.run_duration_seconds = run_duration_seconds
        self.last_check_ts = 0
        self.last_circ_ts = 0
        self.is_on = False

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

    def run(self):
        if timestamp() < (self.last_check_ts  + self.run_every_seconds):
            return

        self.last_check_ts = timestamp()

        if not self.is_on and timestamp() > (self.last_circ_ts + self.on_every_seconds):
            self.turn_on()
            self.last_circ_ts = timestamp()
        elif self.is_on and timestamp() > (self.last_circ_ts + self.run_duration_seconds):
            self.turn_off()

    def turn_on(self):       
        GPIO.output(self.power_pin, GPIO.LOW)
        self.is_on = True
        logging.info("Turned circulation fans on")

    def turn_off(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.is_on = False
        logging.info("Turned circulation fans off")

    def shutdown(self):
        if self.is_on:
            self.turn_off()


class AtticFanTask:
    def __init__(self, run_every_seconds, power_pin, temp_humid_sensor: TempHumidSensor, config, windows):
        self.temp_humid_sensor = temp_humid_sensor
        self.run_every_seconds = run_every_seconds
        self.power_pin = power_pin
        self.is_on = False
        self.last_run_ts = 0
        self.config = config
        self.windows = windows

        logging.info('Setting up fan on pin %d', self.power_pin)

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

    def run(self):
        if timestamp() < (self.last_run_ts + self.run_every_seconds):
            return
 
        self.last_run_ts = timestamp()

        temp_now = self.temp_humid_sensor.get_last_reading()

        if not temp_now:
            return

        temp_f_now = temp_now.get_temp()

        logging.debug('(fan) Current temp: ' + str(temp_f_now))
        logging.debug('(fan) Fan is: ' + ('on' if self.is_on else 'off'))

        # If windows are closed and the temperature has crept to 5 degrees before fan comes on, open the windows
        if not self.windows.eligible_for_open() and temp_f_now > self.config.fan_temp - 5:
            self.windows.open()

        if self.is_on and temp_f_now < self.config.fan_temp:
            self.turn_off()

            ## If it's likely the last fan of the day, close the windows to try to keep heat in.
            if self.windows.eligible_for_close() and current_hour() > 16:
                self.windows.close()

        elif not self.is_on and temp_f_now > self.config.fan_temp:
            self.turn_on()            

        # ultimate fallback
        if self.windows.eligible_for_close() and temp_f_now < self.config.fan_temp - 5:
            self.windows.close()

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

    def __init__(self, run_every_seconds: int, sensor: TempHumidSensor, url: str, web_client: WebClient, location):
        self.run_every_seconds = run_every_seconds
        self.sensor = sensor
        self.last_run_ts = 0
        self.url = url
        self.web_client = web_client
        self.location = location

    def should_run(self):
        return timestamp() > (self.last_run_ts + self.run_every_seconds)

    def run(self) -> bool:
        if not self.should_run():
            return False

        reading = self.sensor.read()
        if not reading:
            return False

        logging.info('read temp/humid at %s: %s' % (self.location, reading.to_string()))
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
        if not self.valve_config:
            return "UNKNOWN"

        return self.valve_config.description

    def open(self, open_duration_seconds = -1):
        GPIO.output(self.signal_pin, GPIO.LOW)
        self.is_open = True
        self.last_opened_time = timestamp()
        if int(open_duration_seconds) > 0:
            self.override_open_duration_seconds = open_duration_seconds
 
        event_client.log_valve_event(self.id, True)
        logging.info('Valve for %s opened', self.get_description())
        logging.debug('Sleeping 1 second')
        time.sleep(VALVE_CLEAR_SLEEP_SECONDS)

    def close(self):
        logging.debug('Sleeping 1 second')
        time.sleep(VALVE_CLEAR_SLEEP_SECONDS)
        GPIO.output(self.signal_pin, GPIO.HIGH)
        self.is_open = False
        self.override_open_duration_seconds = -1
        event_client.log_valve_event(self.id, False)
        logging.info('Valve for %s closed', self.get_description())

class Pump:
    def __init__(self, power_pin: int):
        self.power_pin = power_pin
        self.test_mode = False
        logging.info("Setting up pump on pin %d" % power_pin)

        self.pump_on = False
        self.last_on_ts = -1

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

    def enable_test_mode(self):
        self.test_mode = True

    def turn_on(self):
        if not self.test_mode:
            GPIO.output(self.power_pin, GPIO.LOW)
    
        self.pump_on = True
        self.last_on_ts = timestamp()
        logging.info("Turned on pump")

    def turn_off(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.pump_on = False
        logging.info("Turned off pump")

class Window:
    def __init__(self, input_a, input_b, descriptor, movement_seconds):
        self.input_a = input_a
        self.input_b = input_b
        self.descriptor = descriptor
        self.movement_seconds = movement_seconds

        self.is_open = None

        GPIO.setup(self.input_a, GPIO.OUT)
        GPIO.output(self.input_a, GPIO.LOW)

        GPIO.setup(self.input_b, GPIO.OUT)
        GPIO.output(self.input_b, GPIO.LOW)

        logging.info("Setting up %s on pins %d and %d" % (self.descriptor, self.input_a, self.input_b))

    def eligible_for_open(self):
        return self.is_open is None or self.is_open == False

    def eligible_for_close(self):
        return self.is_open is None or self.is_open == True

    def open(self):
        if not self.eligible_for_open():
            logging.info("Window %s is already open" % self.descriptor)
            return

        logging.info("Opening window %s" % self.descriptor)
        GPIO.output(self.input_a, GPIO.HIGH)
        GPIO.output(self.input_b, GPIO.LOW)
        time.sleep(self.movement_seconds)
        GPIO.output(self.input_a, GPIO.LOW)
        self.is_open = True

    def close(self):
        if not self.eligible_for_close():
            logging.info("Window %s already closed" % self.descriptor)
            return

        logging.info("Closing window %s" % self.descriptor)
        GPIO.output(self.input_a, GPIO.LOW)
        GPIO.output(self.input_b, GPIO.HIGH)
        time.sleep(self.movement_seconds)
        GPIO.output(self.input_b, GPIO.LOW)
        self.is_open = False


class WindowsGroup:
    def __init__(self, windows_list):
       self.windows = windows_list
       self.windows_are_open = None
    
    def eligible_for_open(self):
        if self.windows_are_open is None or self.windows_are_open == False:
            return True

        return False

    def eligible_for_close(self):
        if self.windows_are_open is None or self.windows_are_open == True:
            return True
        return False

    def open(self):
        if not self.eligible_for_open():
            logging.info("Windows are already open")
            return

        for window in self.windows:
            window.open()

        self.windows_are_open = True
   
    def close(self):
        if not self.eligible_for_close():
           logging.info("Windows are already closed")
           return

        for window in self.windows:
            window.close()

        self.windows_are_open = False


class ValveCloseTask:
    def __init__(self, valve: Valve, valve_lock: ValveLock, config, pump: Pump):
        self.valve = valve
        self.valve_lock = valve_lock
        self.config = config
        self.pump = pump

    def run(self):
        #if int(self.valve.override_open_duration_seconds) < 0:
        #    closing_time = self.valve.last_opened_time + self.config.get_valve_config(self.valve.id).open_duration_seconds
        #else:
        #    closing_time = self.valve.last_opened_time + int(self.valve.override_open_duration_seconds)

        closing_time = self.valve.last_opened_time + self.config.get_valve_config(self.valve.id).open_duration_seconds

        if self.valve.is_open:
            logging.debug('Right now its %d, will close valve at %d', timestamp(), int(closing_time))

        if self.valve.is_open and timestamp() > int(closing_time):
            self.pump.turn_off()
            self.valve.close()
            self.valve_lock.release_lock(self.valve.id)
            return True

        return False

class WaterQueueTask:
    def __init__(self, web_client, run_every_seconds, valve_lock, valve_dict, pump: Pump):
        self.web_client = web_client
        self.run_every_seconds = int(run_every_seconds)
        self.last_run_ts = 0
        self.valve_lock = valve_lock
        self.valve_dict = valve_dict
        self.pump = pump

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
        open_duration_seconds = watering_queue[0]['open_duration_seconds']
        if self.valve_lock.acquire_lock(next_valve_id):
#            url = SERVER_URL + '/valves/watering-queue/%s' % next_valve_id
#            response = requests.delete(url)
#
#            if response.status_code != 200:
#                logging.error('Error received trying to dequeue valve')
#                logging.error(response.json())
#                return

            if not self.web_client.dequeue_valve(next_valve_id):
                return

            self.valve_dict[str(next_valve_id)].open(open_duration_seconds)
            self.pump.turn_on()

class WaterPlantsTask:

    """
    example schedule condition
    {
        'hour': 6,
        'water_every_days': 1,
        'water_if_temp': 50     # Didnt do this one yet
    }
    """

    def __init__(self, run_every_seconds, web_client, schedule_conditions_list):
        self.run_every_seconds = run_every_seconds
        self.last_evaluated_timestamp = 0
        self.last_watered_hour = 0
        self.last_watered_day = 0
        self.web_client = web_client
        self.schedule_conditions_list = schedule_conditions_list

        self.load_data()

    def persist_data(self, last_watered_hour, last_watered_day):
        data = {'last_watered_hour': last_watered_hour, 'last_watered_day': last_watered_day}

        with open('water_plants_task.json', 'w') as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists('water_plants_task.json'):
            with open('water_plants_task.json', 'r') as f:
                data = json.load(f)

            self.last_watered_hour = data['last_watered_hour']
            self.last_watered_day = data['last_watered_day']

            logging.info('loaded last watered schedule: %s' % json.dumps(data, indent=2))


    def run(self):
        if timestamp() < (self.last_evaluated_timestamp + self.run_every_seconds):
            return False
        
        self.last_evaluated_timestamp = timestamp()
        
        for sc in self.schedule_conditions_list:
            hour = int(sc['hour'])
            water_every_days = int(sc['water_every_days'])

            comparison = {
                'current_day': current_day(),
                'current_hour': current_hour(),
                'last_watered_hour': self.last_watered_hour,
                'last_watered_day': self.last_watered_day
            }

            logging.debug('comparing %s and %s' % (json.dumps(comparison, indent=2), json.dumps(sc, indent=2)))

            if current_hour() == hour \
              and hour != self.last_watered_hour \
              and current_day() >= (self.last_watered_day + water_every_days):
                  self.last_watered_day = current_day()
                  self.last_watered_hour = current_hour()

                  # Persist last watered hour and day in order to ensure we don't double water if something goes wrong.
                  self.persist_data(self.last_watered_hour, self.last_watered_day) 

                  self.web_client.water_all()
                  logging.info("Queued all plants to be watered.  %s" % json.dumps(sc, indent=2))         

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


class WebClientTester:

    def __init__(self, queue):
        self.queue = queue

    def format_temp_humidity_data_string(self, reading: TempHumidReading):
         return "&th|{timestamp}|humidity:{h}|temp:{t}|heat-index:{hi}".format(timestamp=timestamp(), h=reading.get_humidity(), t=reading.get_temp(), hi=reading.get_heat_index())

    def send_temp_humidity_reading(self, reading: TempHumidReading, url: str):
        data = self.format_temp_humidity_data_string(reading)
        logging.debug('sent web request: %s -> %s', url, data)


    def read_valve_config(self):
        return ""

    def read_fan_config(self):
        return ""

    def read_watering_queue(self):
        return self.queue

    def post_event(self, payload):
        return response.status_code == 200

    def water_all(self):
        return response.status_code == 200

    def dequeue_valve(self, valve_id):
        self.queue = self.queue[1::]
        return True

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    task_coordinator.shutdown()
    GPIO.cleanup()
    sys.exit(0)

########################################
################# SET UP ###############
########################################

def operation_normal():
    tempHumidInside = TempHumidSensor(PIN_TEMP_HUMIDITY_INSIDE)
    #tempHumidOutside = TempHumidSensor(PIN_TEMP_HUMIDITY_OUTSIDE)
    web_client = WebClient()

    config = Config()

    config_sync_task = ConfigSyncTask(FIFTEEN_MINUTES, web_client, config)

    # Grab initial settings for valves
    config_sync_task.run()

    valve_lock = ValveLock()
    valve_1 = Valve(1, PIN_VALVE_1_POWER, config.get_valve_config(1))
    valve_2 = Valve(2, PIN_VALVE_2_POWER, config.get_valve_config(2))
    valve_3 = Valve(3, PIN_VALVE_3_POWER, config.get_valve_config(3))
    valve_4 = Valve(4, PIN_VALVE_4_POWER, config.get_valve_config(4))
    valve_5 = Valve(5, PIN_VALVE_5_POWER, config.get_valve_config(5))
    valve_6 = Valve(6, PIN_VALVE_6_POWER, config.get_valve_config(6))
    valve_7 = Valve(7, PIN_VALVE_7_POWER, config.get_valve_config(7))
    valve_8 = Valve(8, PIN_VALVE_8_POWER, config.get_valve_config(8))

    valve_dict = {
        '1': valve_1, 
        '2': valve_2, 
        '3': valve_3, 
        '4': valve_4, 
        '5': valve_5,
        '6': valve_6,
        '7': valve_7, 
        '8': valve_8, 
    }

    watering_schedule = [
        {
            'hour': 7,
            'water_every_days': 1
        }
    ]
    
    pump = Pump(PIN_PUMP_POWER)

    window_se = Window(PIN_WINDOW_SE_INPUT_A, PIN_WINDOW_SE_INPUT_B, 'Window[SouthEast]', 20)
    windows_group = WindowsGroup([window_se])

    task_coordinator.register_task(config_sync_task)
    task_coordinator.register_task(TempHumidLogTask(FIVE_MINUTES, tempHumidInside, SERVER_URL + URL_TEMP_HUMID_INSIDE, web_client, 'inside'))
    task_coordinator.register_task(AtticFanTask(60, PIN_FAN_POWER, tempHumidInside, config, windows_group))
    #task_coordinator.register_task(TempHumidLogTask(FIVE_MINUTES, tempHumidOutside, SERVER_URL + URL_TEMP_HUMID_OUTSIDE, web_client, 'outside'))
    task_coordinator.register_task(WaterPlantsTask(TEN_MINUTES, web_client, watering_schedule))
    task_coordinator.register_task(WaterQueueTask(web_client, 30, valve_lock, valve_dict, pump))
    task_coordinator.register_task(ValveCloseTask(valve_1, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_2, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_3, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_4, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_5, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_6, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_7, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve_8, valve_lock, config, pump))
    task_coordinator.register_task(EventSendingTask(60, web_client))
    ## Check every 30 seconds to run the circ fans  for 90 seconds every 10 minutes:
    #task_coordinator.register_task(CirculatorFansTask(30, PIN_CIRC_FAN_POWER, TEN_MINUTES, 90))

    task_coordinator.run()

def operation_seedlings():
    task_coordinator.register_task(GrowLightTask('05:00', '20:00', 26))
    task_coordinator.run()

def operation_valve_test():
    open_duration_seconds = 12

    configuration = [
                {
                    "valve_id": 1,
                    "description": "VALVE1",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 2,
                    "description": "VALVE2",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 3,
                    "description": "VALVE3",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 4,
                    "description": "VALVE4",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 5,
                    "description": "VALVE5",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 6,
                    "description": "VALVE6",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 7,
                    "description": "VALVE7",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                },
                {
                    "valve_id": 8,
                    "description": "VALVE8",
                    "conductivity_threshold": 0.6,
                    "watering_delay_seconds": 10,
                    "open_duration_seconds": open_duration_seconds
                }
    ]

    config = Config()
    config.update_valve_config(configuration)

    valve1 = Valve(1, PIN_VALVE_1_POWER, config.get_valve_config(1))
    valve2 = Valve(2, PIN_VALVE_2_POWER, config.get_valve_config(2))
    valve3 = Valve(3, PIN_VALVE_3_POWER, config.get_valve_config(3))
    valve4 = Valve(4, PIN_VALVE_4_POWER, config.get_valve_config(4))
    valve5 = Valve(5, PIN_VALVE_5_POWER, config.get_valve_config(5))
    valve6 = Valve(6, PIN_VALVE_6_POWER, config.get_valve_config(6))
    valve7 = Valve(7, PIN_VALVE_7_POWER, config.get_valve_config(7))
    valve8 = Valve(8, PIN_VALVE_8_POWER, config.get_valve_config(8))

    valve_lock = ValveLock()
    valve_dict = {
        '1': valve1, 
        '2': valve2, 
        '3': valve3, 
        '4': valve4,
        '5': valve5,
        '6': valve6,
        '7': valve7, 
        '8': valve8, 
    }

    valveQueue = [
        #{            'valve_id': 1,            'open_duration_seconds': open_duration_seconds        },
        #{            'valve_id': 2,            'open_duration_seconds': open_duration_seconds        },
        #{            'valve_id': 3,            'open_duration_seconds': open_duration_seconds        },
        #{            'valve_id': 4,            'open_duration_seconds': open_duration_seconds        },
        {            'valve_id': 5,            'open_duration_seconds': open_duration_seconds        },
        {            'valve_id': 6,            'open_duration_seconds': open_duration_seconds        },
        {            'valve_id': 7,            'open_duration_seconds': open_duration_seconds        },
        {            'valve_id': 8,            'open_duration_seconds': open_duration_seconds        },
    ]

    # For testing individual:
    #valveQueue = [{'valve_id': 8, 'open_duration_seconds': open_duration_seconds}]

    pump = Pump(PIN_PUMP_POWER)
    #pump.enable_test_mode()
    
    waterQueue = WaterQueueTask(WebClientTester(valveQueue), 30, valve_lock, valve_dict, pump)

    task_coordinator.register_task(waterQueue)
    task_coordinator.register_task(ValveCloseTask(valve1, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve2, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve3, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve4, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve5, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve6, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve7, valve_lock, config, pump))
    task_coordinator.register_task(ValveCloseTask(valve8, valve_lock, config, pump))
    
    task_coordinator.run()

############################
### MAIN EXECUTION BELOW ###
############################
logging.info('Starting up...')
signal.signal(signal.SIGINT, signal_handler)

# use the numbers printed on the guides, not the ones on the board
GPIO.setmode(GPIO.BCM)

operation_normal()
#operation_seedings()
#operation_valve_test()

GPIO.cleanup()
exit(0)
