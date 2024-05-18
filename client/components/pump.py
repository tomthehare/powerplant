from logging import Logger
import RPi.GPIO as GPIO

from components.time_observer import TimeObserver
from gpio_controller import GPIOController


class Pump:
    def __init__(
        self, power_pin: int, logger: Logger, time_observer: TimeObserver = None
    ):
        self.power_pin = power_pin
        self.test_mode = False
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

        self.logger.info("Setting up pump on pin %d" % power_pin)

        self.pump_on = False
        self.last_on_ts = -1

        GPIOController.register_pin(self.power_pin)
        GPIOController.activate_pin(self.power_pin)

    def enable_test_mode(self):
        self.test_mode = True

    def turn_on(self):
        if not self.test_mode:
            GPIOController.deactivate_pin(self.power_pin)
        self.pump_on = True
        self.last_on_ts = self.time_observer.timestamp()
        self.logger.info("Turned on pump")

    def turn_off(self):
        GPIOController.activate_pin(self.power_pin)
        self.pump_on = False
        self.logger.info("Turned off pump")

    def is_pump_on(self) -> bool:
        return self.pump_on

    def is_pump_off(self) -> bool:
        return not self.is_pump_on()
