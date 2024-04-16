from logging import Logger
from client.components.time_observer import TimeObserver
from client.dtos.temp_humid_reading import TempHumidReading
import requests


class WebClient:

    def __init__(
        self, server_url: str, logger: Logger, time_observer: TimeObserver = None
    ):
        self.server_url = server_url
        self.logger = logger
        self.time_observer = time_observer if time_observer else TimeObserver()

    def send_temp_humidity_reading(self, reading: TempHumidReading, url: str, location: str):
        self.logger.debug("sent web request: %s -> %s", url, str(TempHumidReading))
        payload = {
            "timestamp": reading.read_at_ts,
            "humidity": reading.humid,
            "temperature": reading.get_temp(),
            "location": location
        }
        r = requests.post(url, data=payload)

        if r.status_code != 200 and r.status_code != 201:
            self.logger.error("Temp/humid recording failed: %s" % r.json())

    def read_valve_config(self):
        url = self.server_url + "/valve-config"
        r = requests.get(url)

        return r.json()

    def read_fan_config(self):
        url = self.server_url + "/fan-config"
        response = requests.get(url)

        return response.json()

    def read_watering_queue(self):
        url = self.server_url + "/valves/watering-queue"

        response = requests.get(url)
        return response.json()

    def post_event(self, payload):
        url = self.server_url + "/events"

        response = requests.post(url, data=payload)

        if response.status_code != 200:
            self.logger.error("Error posting event: %s" % response.json())

        return response.status_code == 200

    def water_all(self):
        url = self.server_url + "/valves/water"

        response = requests.post(url)

        return response.status_code == 200

    def dequeue_valve(self, valve_id):
        url = self.server_url + "/valves/watering-queue/%s" % valve_id
        response = requests.delete(url)

        if response.status_code != 200:
            self.logger.error("Error received trying to dequeue valve")
            self.logger.error(response.json())
            return False

        return True
