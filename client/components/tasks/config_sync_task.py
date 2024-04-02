from logging import Logger
import json

from client.components.config import Config
from client.components.time_observer import TimeObserver
from client.components.web_client import WebClient


class ConfigSyncTask:
    def __init__(
        self,
        run_every_seconds: int,
        web_client: WebClient,
        config: Config,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.run_every_seconds = run_every_seconds
        self.last_run_ts = 0
        self.web_client = web_client
        self.config = config
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

    def should_run(self):
        return self.time_observer.timestamp() > (
            self.last_run_ts + self.run_every_seconds
        )

    def run(self):
        if not self.should_run():
            return

        new_config = self.web_client.read_valve_config()
        self.logger.debug("Got new valve config: " + json.dumps(new_config, indent=2))
        self.config.update_valve_config(new_config)

        new_fan_config = self.web_client.read_fan_config()
        self.logger.debug("Got new fan config: " + json.dumps(new_fan_config, indent=2))
        self.config.update_fan_temp_config(new_fan_config)

        self.last_run_ts = self.time_observer.timestamp()
