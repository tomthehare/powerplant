from logging import Logger

import RPi.GPIO as GPIO

from components.event_client import EventClient
from components.time_observer import TimeObserver
from gpio_controller import GPIOController
from window_config import WindowConfig


class Window:
    def __init__(
        self,
        window_config: WindowConfig,
        logger: Logger,
        event_client: EventClient,
        time_observer: TimeObserver = None,
    ):
        self.input_a = window_config.pin_1
        self.input_b = window_config.pin_2
        self.descriptor = window_config.window_name
        self.movement_seconds = window_config.movement_seconds
        self.logger = logger
        self.event_client = event_client or EventClient()
        self.time_observer = time_observer or TimeObserver()

        self.is_open = None

        GPIOController.register_pin(self.input_a)
        GPIOController.deactivate_pin(self.input_a)

        GPIOController.register_pin(self.input_b)
        GPIOController.deactivate_pin(self.input_b)

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
        GPIOController.activate_pin(self.input_a)
        GPIOController.deactivate_pin(self.input_b)

        self.time_observer.sleep(self.movement_seconds)

        GPIOController.deactivate_pin(self.input_a)
        self.is_open = True
        self.event_client.log_window_opened_event(self.descriptor)

    def close(self):
        if not self.eligible_for_close():
            self.logger.info("Window %s already closed" % self.descriptor)
            return

        self.logger.info("Closing window %s" % self.descriptor)
        GPIOController.deactivate_pin(self.input_a)
        GPIOController.activate_pin(self.input_b)

        self.time_observer.sleep(self.movement_seconds)

        GPIOController.deactivate_pin(self.input_b)
        self.is_open = False
        self.event_client.log_window_closed_event(self.descriptor)
