from logging import Logger
import time

import RPi.GPIO as GPIO

from components.event_client import EventClient
from components.time_observer import TimeObserver
from dtos.valve_config import ValveConfig
from gpio_controller import GPIOController


class Valve:
    VALVE_CLEAR_SLEEP_SECONDS = 2

    def __init__(
        self,
        valve_id: int,
        signal_pin: int,
        valve_config: ValveConfig,
        logger: Logger,
        event_client: EventClient,
        time_observer: TimeObserver = None,
    ):
        self.last_opened_time = 0
        self.id = valve_id
        self.is_open = False
        self.signal_pin = signal_pin
        self.valve_config = valve_config
        self.override_open_duration_seconds = -1
        self.logger = logger
        self.event_client = event_client
        self.time_observer = time_observer or TimeObserver()

        self.logger.info(
            "Setting up %s valve on pin %d", self.get_description(), self.signal_pin
        )

        GPIOController.register_pin(self.signal_pin)
        GPIOController.activate_pin(self.signal_pin)

    def get_description(self):
        if not self.valve_config:
            return "UNKNOWN"

        return self.valve_config.description

    def open(self, open_duration_seconds=-1):
        GPIOController.deactivate_pin(self.signal_pin)
        self.is_open = True
        self.last_opened_time = self.time_observer.timestamp()
        if int(open_duration_seconds) > 0:
            self.override_open_duration_seconds = open_duration_seconds

        self.event_client.log_valve_event(self.id, True)
        self.logger.info("Valve for %s opened", self.get_description())
        self.logger.debug("Sleeping 1 second")
        time.sleep(self.VALVE_CLEAR_SLEEP_SECONDS)

    def close(self):
        self.logger.debug("Sleeping 1 second")
        time.sleep(self.VALVE_CLEAR_SLEEP_SECONDS)
        GPIOController.activate_pin(self.signal_pin)
        self.is_open = False
        self.override_open_duration_seconds = -1
        self.event_client.log_valve_event(self.id, False)
        self.logger.info("Valve for %s closed", self.get_description())
