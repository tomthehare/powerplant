from logging import Logger

from client.components.config import Config
from client.components.event_client import EventClient
from client.components.temp_humid_sensor import TempHumidSensor
import RPi.GPIO as GPIO

from client.components.time_observer import TimeObserver
from client.components.windows_group import WindowsGroup


class AtticFanTask:
    def __init__(
        self,
        task_cycle_seconds: int,
        power_pin: int,
        temp_humid_sensor: TempHumidSensor,
        config: Config,
        windows: WindowsGroup,
        logger: Logger,
        event_client: EventClient,
        time_observer: TimeObserver = None,
    ):
        self.temp_humid_sensor = temp_humid_sensor
        self.task_cycle_seconds = task_cycle_seconds
        self.power_pin = power_pin
        self.is_on = False
        self.last_run_ts = 0
        self.config = config
        self.windows = windows
        self.logger = logger
        self.event_client = event_client
        self.time_observer = time_observer or TimeObserver()

        self.logger.info("Setting up fan on pin %d", self.power_pin)

        GPIO.setup(self.power_pin, GPIO.OUT)
        GPIO.output(self.power_pin, GPIO.HIGH)

    def run(self):
        if self.time_observer.timestamp() < (
            self.last_run_ts + self.task_cycle_seconds
        ):
            return

        self.last_run_ts = self.time_observer.timestamp()

        temp_now = self.temp_humid_sensor.get_last_reading()

        if not temp_now:
            return

        temp_f_now = temp_now.get_temp()

        self.logger.debug("(fan) Current temp: " + str(temp_f_now))
        self.logger.debug("(fan) Fan is: " + ("on" if self.is_on else "off"))

        # If windows are closed and the temperature has crept to 5 degrees before fan comes on, open the windows
        if (
            self.windows.eligible_for_open()
            and temp_f_now > (self.config.fan_temp - 5)
            and self.time_observer.current_hour() < 16
        ):
            self.windows.open()

        if self.is_on and temp_f_now < self.config.fan_temp:
            self.turn_off()

            # If it's likely the last fan of the day, close the windows to try to keep heat in.
            if (
                self.windows.eligible_for_close()
                and self.time_observer.current_hour() >= 16
            ):
                self.windows.close()

        elif (
            not self.is_on
            and temp_f_now > self.config.fan_temp
            and self.time_observer.current_hour() < 16
        ):
            self.turn_on()

            # ultimate fallback
        if (
            self.windows.eligible_for_close()
            and not self.is_on
            and (
                temp_f_now < (self.config.fan_temp - 5)
                or self.time_observer.current_hour() >= 16
            )
        ):
            self.windows.close()

    def turn_on(self):
        GPIO.output(self.power_pin, GPIO.LOW)
        self.is_on = True
        self.event_client.log_fan_event(True)
        self.logger.info("Turned fan on")

    def turn_off(self):
        GPIO.output(self.power_pin, GPIO.HIGH)
        self.is_on = False
        self.event_client.log_fan_event(False)
        self.logger.info("Turned fan off")

    def shutdown(self):
        if self.is_on:
            self.turn_off()
