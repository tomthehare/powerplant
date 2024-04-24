from logging import Logger

import RPi.GPIO as GPIO

from components.time_observer import TimeObserver


class Window:
    def __init__(
        self,
        input_a: int,
        input_b: int,
        descriptor: str,
        movement_seconds: int,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.input_a = input_a
        self.input_b = input_b
        self.descriptor = descriptor
        self.movement_seconds = movement_seconds
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

        self.is_open = None

        GPIO.setup(self.input_a, GPIO.OUT)
        GPIO.output(self.input_a, GPIO.LOW)

        GPIO.setup(self.input_b, GPIO.OUT)
        GPIO.output(self.input_b, GPIO.LOW)

        self.logger.info(
            "Setting up %s on pins %d and %d"
            % (self.descriptor, self.input_a, self.input_b)
        )

    def eligible_for_open(self):
        return self.is_open is None or self.is_open == False

    def eligible_for_close(self):
        return self.is_open is None or self.is_open == True

    def open(self):
        if not self.eligible_for_open():
            self.logger.info("Window %s is already open" % self.descriptor)
            return

        self.logger.info("Opening window %s" % self.descriptor)
        GPIO.output(self.input_a, GPIO.HIGH)
        GPIO.output(self.input_b, GPIO.LOW)
        self.time_observer.sleep(self.movement_seconds)
        GPIO.output(self.input_a, GPIO.LOW)
        self.is_open = True

    def close(self):
        if not self.eligible_for_close():
            self.logger.info("Window %s already closed" % self.descriptor)
            return

        self.logger.info("Closing window %s" % self.descriptor)
        GPIO.output(self.input_a, GPIO.LOW)
        GPIO.output(self.input_b, GPIO.HIGH)
        self.time_observer.sleep(self.movement_seconds)
        GPIO.output(self.input_b, GPIO.LOW)
        self.is_open = False
