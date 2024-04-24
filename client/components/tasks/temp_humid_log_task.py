from logging import Logger

from components.temp_humid_sensor import TempHumidSensor
from components.time_observer import TimeObserver
from components.web_client import WebClient


class TempHumidLogTask:

    def __init__(
        self,
        task_cycle_seconds: int,
        sensor: TempHumidSensor,
        url: str,
        web_client: WebClient,
        location: str,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.task_cycle_seconds = task_cycle_seconds
        self.sensor = sensor
        self.last_run_ts = 0
        self.url = url
        self.web_client = web_client
        self.location = location
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

    def should_run(self):
        return self.time_observer.timestamp() > (
            self.last_run_ts + self.task_cycle_seconds
        )

    def run(self) -> bool:
        if not self.should_run():
            return False

        reading = self.sensor.read()
        if not reading:
            return False

        self.logger.info(
            "read temp/humid at %s: %s" % (self.location, reading.to_string())
        )
        self.web_client.send_temp_humidity_reading(reading, self.url, self.location)
        self.last_run_ts = self.time_observer.timestamp()

        return True
