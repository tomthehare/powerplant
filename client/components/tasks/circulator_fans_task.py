from logging import Logger

import RPi.GPIO as GPIO

from components.time_observer import TimeObserver
from gpio_controller import GPIOController


class CirculatorFansTask:
    def __init__(
        self,
        task_cycle_in_seconds: int,
        power_pin: int,
        on_every_seconds: int,
        run_duration_seconds: int,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.task_cycle_in_seconds = task_cycle_in_seconds
        self.power_pin = power_pin
        self.on_every_seconds = on_every_seconds
        self.run_duration_seconds = run_duration_seconds
        self.last_check_ts = 0
        self.last_circ_ts = 0
        self.is_on = False
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

        GPIOController.register_pin(self.power_pin)
        GPIOController.activate_pin(self.power_pin)

    def run(self):
        if self.time_observer.timestamp() < (
            self.last_check_ts + self.task_cycle_in_seconds
        ):
            return

        self.last_check_ts = self.time_observer.timestamp()

        if not self.is_on and self.time_observer.timestamp() > (
            self.last_circ_ts + self.on_every_seconds
        ):
            self.turn_on()
            self.last_circ_ts = self.time_observer.timestamp()
        elif self.is_on and self.time_observer.timestamp() > (
            self.last_circ_ts + self.run_duration_seconds
        ):
            self.turn_off()

    def turn_on(self):
        GPIOController.deactivate_pin(self.power_pin)
        self.is_on = True
        self.logger.info("Turned circulation fans on")

    def turn_off(self):
        GPIOController.activate_pin(self.power_pin)
        self.is_on = False
        self.logger.info("Turned circulation fans off")

    def shutdown(self):
        if self.is_on:
            self.turn_off()
