from logging import Logger
from components.time_observer import TimeObserver
from components.web_client import WebClient
from dtos.temp_humid_reading import TempHumidReading


class FakeWebClient(WebClient):

    def __init__(
        self,
        server_url: str,
        logger: Logger,
        queue: list,
        time_observer: TimeObserver = None,
    ):
        super().__init__(server_url, logger, time_observer)
        self.queue = queue

    def format_temp_humidity_data_string(self, reading: TempHumidReading):
        return "its all made up"

    def send_temp_humidity_reading(self, reading: TempHumidReading, url: str):
        pass

    def ask_if_plants_need_water(self, descriptor: str) -> bool:
        return False

    def read_watering_queue(self):
        return self.queue

    def read_fan_config(self):
        return []

    def post_event(self, payload):
        return True

    def water_all(self):
        return True

    def dequeue_valve(self, valve_id):
        return True
