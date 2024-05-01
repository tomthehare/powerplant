import json
from logging import Logger
import os

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
        schedule_conditions_list,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.run_every_seconds = run_every_seconds
        self.last_evaluated_timestamp = 0
        self.last_watered_hour = 0
        self.last_watered_day = 0
        self.web_client = web_client
        self.schedule_conditions_list = schedule_conditions_list
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

        for sc in self.schedule_conditions_list:
            hour = int(sc["hour"])
            water_every_days = int(sc["water_every_days"])

            comparison = {
                "current_day": self.time_observer.current_day(),
                "current_hour": self.time_observer.current_hour(),
                "last_watered_hour": self.last_watered_hour,
                "last_watered_day": self.last_watered_day,
            }

            self.logger.debug(
                "comparing %s and %s"
                % (json.dumps(comparison, indent=2), json.dumps(sc, indent=2))
            )

            if (
                self.time_observer.current_hour() == hour
                and self.time_observer.current_day()
                >= (self.last_watered_day + water_every_days)
            ):
                self.last_watered_day = self.time_observer.current_day()
                self.last_watered_hour = self.time_observer.current_hour()

                # Persist last watered hour and day in order to ensure we don't double water if something goes wrong.
                self.persist_data(self.last_watered_hour, self.last_watered_day)

                self.web_client.water_all()
                self.logger.info(
                    "Queued all plants to be watered.  %s" % json.dumps(sc, indent=2)
                )

        return True
