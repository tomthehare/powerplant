from logging import Logger
from client.components.time_observer import TimeObserver
import RPi.GPIO as GPIO


class GrowLightTask:
    def __init__(
        self,
        time_on: str,
        time_off: str,
        power_pin: int,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

        time_on_pieces = time_on.split(":")
        time_off_pieces = time_off.split(":")

        self.time_on_hour = int(time_on_pieces[0])
        self.time_on_minute = int(time_on_pieces[1])

        self.time_off_hour = int(time_off_pieces[0])
        self.time_off_minute = int(time_off_pieces[1])

        self.light_on = False
        self.power_pin = power_pin

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

        self.logger.info(
            "Light set to turn on at %d:%d and turn off at %d:%d"
            % (
                self.time_on_hour,
                self.time_on_minute,
                self.time_off_hour,
                self.time_off_minute,
            )
        )

    def should_be_on(self):
        turn_on_min_timestamp = (self.time_on_hour * 60) + self.time_on_minute
        turn_off_min_timestamp = (self.time_off_hour * 60) + self.time_off_minute
        now_min_timestamp = (
            self.time_observer.current_hour() * 60
        ) + self.time_observer.current_minute()

        return (
            turn_on_min_timestamp <= now_min_timestamp
            and now_min_timestamp < turn_off_min_timestamp
        )

    def should_be_off(self):
        return not self.should_be_on()

    def turn_off_light(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.light_on = False
        self.logger.info("turned off the grow lights")

    def turn_on_light(self):
        GPIO.output(self.power_pin, GPIO.LOW)
        self.light_on = True
        self.logger.info("turned on the grow lights")

    def run(self):
        if self.light_on and self.should_be_off():
            self.turn_off_light()
        elif not self.light_on and self.should_be_on():
            self.turn_on_light()
