from logging import Logger
import RPi.GPIO as GPIO

from client.components.time_observer import TimeObserver


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

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

    def enable_test_mode(self):
        self.test_mode = True

    def turn_on(self):
        if not self.test_mode:
            GPIO.output(self.power_pin, GPIO.LOW)

        self.pump_on = True
        self.last_on_ts = self.time_observer.timestamp()
        self.logger.info("Turned on pump")

    def turn_off(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.pump_on = False
        self.logger.info("Turned off pump")
