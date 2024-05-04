from logging import Logger

from components.config import Config
from components.event_client import EventClient
from components.fake_web_client import FakeWebClient
from components.pump import Pump
from components.task_coordinator import TaskCoordinator
from components.tasks.valve_close_task import ValveCloseTask
from components.tasks.water_queue_task import WaterQueueTask
from components.valve import Valve
from components.valve_lock import ValveLock
from components.window import Window
from components.windows_group import WindowsGroup
from gpio_controller import GPIOController
from pin_config import PinConfig
from window_config import (
    WINDOW_SOUTH_EAST,
    WINDOW_NORTH,
    WINDOW_EAST,
    WINDOW_SOUTH_WEST,
    get_window_config,
)


class WindowTestOperation:

    def __init__(self, server_url: str, logger: Logger):
        self.server_url = server_url
        self.logger = logger

    def run_operation(self):
        GPIOController.set_test_mode(True, self.logger)

        window_se = Window(
            get_window_config(WINDOW_SOUTH_EAST),
            self.logger,
        )

        window_n = Window(
            get_window_config(WINDOW_NORTH),
            self.logger,
        )
        window_sw = Window(
            get_window_config(WINDOW_SOUTH_WEST),
            self.logger,
        )
        window_e = Window(
            get_window_config(WINDOW_EAST),
            self.logger,
        )
        windows_list = [window_se, window_n, window_sw, window_e]
        windows_group = WindowsGroup(windows_list, self.logger)

        # Make sure the windows are closed before doing anything else on start up.
        windows_group.open()

        windows_group.close()
