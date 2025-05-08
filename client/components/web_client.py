from logging import Logger
from components.time_observer import TimeObserver
from dtos.temp_humid_reading import TempHumidReading
import requests


class WebClient:

    def __init__(
        self, server_url: str, logger: Logger, time_observer: TimeObserver = None
    ):
        self.server_url = server_url
        self.logger = logger
        self.time_observer = time_observer if time_observer else TimeObserver()

    def send_temp_humidity_reading(
        self, reading: TempHumidReading, url: str, location: str
    ):
        self.logger.debug("sent web request: %s -> %s", url, str(reading))
        payload = {
            "timestamp": reading.read_at_ts,
            "humidity": reading.humid,
            "temperature": reading.get_temp(),
            "location": location,
        }
        r = requests.post(url, json=payload)

        if r.status_code != 200 and r.status_code != 201:
            self.logger.error("Temp/humid recording failed: %s" % r.json())

    def read_valve_config(self):
        url = self.server_url + "/config"
        r = requests.get(url)

        decoded = r.json()

        return decoded["plant_groups"] if "plant_groups" in decoded else []

    def read_fan_config(self):
        url = self.server_url + "/config"
        response = requests.get(url)

        return response.json()

    def queue_valve_for_water(self, valve_id):
        url = self.server_url + "/watering-queue"

        r = requests.put(url, json={"valve_id": valve_id, "open_duration_seconds": 30})

        return r.status_code == 200

    def read_watering_queue(self):
        url = self.server_url + "/watering-queue"

        response = requests.get(url)
        return response.json()

    def post_event(self, payload):
        url = self.server_url + "/events"

        response = requests.post(url, json=payload)

        if response.status_code not in [200, 201]:
            self.logger.error("Error posting event: %s" % response.json())
            return False

        return True

    def dequeue_valve(self):
        url = self.server_url + "/watering-queue"
        response = requests.delete(url)

        if response.status_code != 200:
            self.logger.error("Error received trying to dequeue valve")
            self.logger.error(response.json())
            return False

        return True

    def ping_server(self) -> bool:
        url = self.server_url

        try:
            response = requests.get(url)
            self.logger.debug("pinged server, got response: %s" % response.json())
        except Exception as e:
            return False

        return "power" in response.json()
