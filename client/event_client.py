import time 
import os
import string
import random
import json
import glob

class EventClient:

    def __init__(self, log_dir = ''):
        self.log_dir = log_dir if log_dir != '' else './events'
        self.fan_event_sync_hash = ''
        self.valve_hashes = {}
        self.window_hashes = {}

    def get_sync_hash(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(10))

    def log_valve_event(self, valve_id, is_open):
        # We will keep track of a common identifier between open and close events in order to get
        # accurate watering time.  if we see an open without a closed or a closed without an open, we can note it
        if is_open:
            self.valve_hashes[valve_id] = self.get_sync_hash()

        event = {
            'subject': 'valve_' + str(valve_id),
            'time': round(time.time()),
            'event': 'opened' if is_open else 'closed',
            'sync_hash': self.valve_hashes[valve_id]
        }

        self.log_event_to_file(event)

    def log_fan_event(self, is_on):
        # We will keep track of a common identifier between on and off events in order to get
        # accurate fan-on-time.  if we see an on without an off or an off without an on, we can note it
        if is_on:
            self.fan_event_sync_hash = self.get_sync_hash()

        event = {
            'subject': 'fan',
            'time': round(time.time()),
            'event': 'turned_on' if is_on else 'turned_off',
            'sync_hash': self.fan_event_sync_hash
        }

        self.log_event_to_file(event)

    def log_window_opened_event(self, window_id):
        self.log_window_event(window_id, True)

    def log_window_closed_event(self, window_id):
        self.log_window_event(window_id, False)

    def log_window_event(self, window_id, opened):
        if opened:
            self.window_hashes[window_id] = self.get_sync_hash()

        event = {
            'subject': 'window',
            'time': round(time.time()),
            'event': 'opened' if opened else 'closed',
            'sync_hash': self.window_hashes[window_id]
        }

        self.log_event_to_file(event)

    def log_event_to_file(self, event_payload):
        file_path = self.log_dir + '/' + str(time.time()) + '.json'

        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        
        with open(file_path, 'w') as f:
            json.dump(event_payload, f)

    def get_earliest_event(self):
        list_of_files = sorted(filter(os.path.isfile, glob.glob(self.log_dir + '/')))

        list_of_files = os.listdir(self.log_dir)

        if not list_of_files:
            return None

        list_of_files = sorted(list_of_files)
        filename = list_of_files[0]

        with open(self.log_dir + '/' + filename, 'r') as f:
            payload = json.load(f)

        return {'filename': filename, 'payload': payload}

    def delete_event(self, filename):
        os.remove(self.log_dir + '/' + filename)
