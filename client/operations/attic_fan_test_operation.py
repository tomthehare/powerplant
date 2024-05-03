from logging import Logger

from components.config import Config
from components.event_client import EventClient
from components.fake_temp_humid_sensor import FakeTempHumidSensor
from components.tasks.attic_fan_task import AtticFanTask
from components.time_observer import TimeObserver
from components.window import Window
from components.windows_group import WindowsGroup
from pin_config import PinConfig
from window_config import (
    WINDOW_NORTH,
    get_window_config,
)


class AtticFanTestOperation:

    def __init__(self, server_url: str, logger: Logger):
        self.server_url = server_url
        self.logger = logger

    def run_operation(self):
        window_n = Window(
            get_window_config(WINDOW_NORTH),
            self.logger,
        )
        windows_group = WindowsGroup([], self.logger)

        attic_fan = AtticFanTask(
            10,
            PinConfig.PIN_FAN_POWER,
            FakeTempHumidSensor(
                PinConfig.PIN_TEMP_HUMIDITY_INSIDE, self.logger, "inside"
            ),
            Config(),
            windows_group,
            self.logger,
            EventClient(),
        )
        time_observer = TimeObserver()
        while True:
            attic_fan.run()
            time_observer.sleep(5)
