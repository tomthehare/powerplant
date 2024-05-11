import json
from logging import Logger
import os

from components.config import Config
from components.time_observer import TimeObserver
from components.web_client import WebClient


class WaterPlantsTask:
    """
    example schedule condition
    {
        'hour': 6,
        'water_every_days': 1,
        'water_if_temp': 50     # Didnt do this one yet
    }
    """

    def __init__(
        self,
        run_every_seconds: int,
        web_client: WebClient,
        config: Config,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.run_every_seconds = run_every_seconds
        self.last_evaluated_timestamp = 0
        self.last_watered_hour = 0
        self.last_watered_day = 0
        self.web_client = web_client
        self.config = config
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

        self.load_data()

    def persist_data(self, last_watered_hour, last_watered_day):
        data = {
            "last_watered_hour": last_watered_hour,
            "last_watered_day": last_watered_day,
        }

        with open("water_plants_task.json", "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("water_plants_task.json"):
            with open("water_plants_task.json", "r") as f:
                data = json.load(f)

            self.last_watered_hour = data["last_watered_hour"]
            self.last_watered_day = data["last_watered_day"]

            self.logger.info(
                "loaded last watered schedule: %s" % json.dumps(data, indent=2)
            )

    def run(self):
        if self.time_observer.timestamp() < (
            self.last_evaluated_timestamp + self.run_every_seconds
        ):
            return False

        self.last_evaluated_timestamp = self.time_observer.timestamp()

        hours = self.config.water_at_hours
        water_every_days = self.config.water_every_days

        comparison = {
            "current_day": self.time_observer.current_day(),
            "current_hour": self.time_observer.current_hour(),
            "last_watered_hour": self.last_watered_hour,
            "last_watered_day": self.last_watered_day,
            "config_hours": hours,
            "config_water_every_days": water_every_days,
        }

        self.logger.debug(comparison)

        if (
            self.time_observer.current_hour() in hours
            and self.time_observer.current_day()
            >= (self.last_watered_day + water_every_days)
        ):
            self.last_watered_day = self.time_observer.current_day()
            self.last_watered_hour = self.time_observer.current_hour()

            # Persist last watered hour and day in order to ensure we don't double water if something goes wrong.
            self.persist_data(self.last_watered_hour, self.last_watered_day)

            # TODO should replace this with active check boxes on teh config screen
            self.web_client.queue_valve_for_water(1)
            self.web_client.queue_valve_for_water(2)
            self.web_client.queue_valve_for_water(4)
            self.web_client.queue_valve_for_water(6)
            self.web_client.queue_valve_for_water(8)

            self.logger.info("Queued all plants to be watered.")

        return True
