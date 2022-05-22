import time 
import os
import string
import random
import json

class EventClient:

    def __init__(self, log_dir = ''):
        self.log_dir = log_dir if log_dir != '' else './events'
        self.fan_event_sync_hash = ''

    def get_sync_hash(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(10))

    def log_fan_event(self, is_on):
        # We will keep track of a common identifier between on and off events in order to get
        # accurate fan-on-time.  if we see an on without an off or an off without an on, we can note it
        if is_on:
            self.fan_event_sync_hash = self.get_sync_hash()

        event = {
            'subject': 'fan',
            'time': round(time.time()),
            'event': 'turned_on' if is_on else 'turned off',
            'sync_hash': self.fan_event_sync_hash
        }

        self.log_event_to_file(event)

    def log_event_to_file(self, event_payload):
        file_path = self.log_dir + '/' + str(time.time()) + '.json'

        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        
        with open(file_path, 'w') as f:
            json.dump(event_payload, f)
