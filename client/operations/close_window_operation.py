from logging import Logger

from components.task_coordinator import TaskCoordinator
from components.window import Window
from components.windows_group import WindowsGroup
from pin_config import PinConfig


class CloseWindowOperation:

    def __init__(self, logger: Logger):
        self.logger = logger

    def run_operation(self, task_coordinator: TaskCoordinator):
        window_se = Window(
            PinConfig.PIN_WINDOW_SE_INPUT_A,
            PinConfig.PIN_WINDOW_SE_INPUT_B,
            "Window[SouthEast]",
            20,
            self.logger,
        )
        window_n = Window(
            PinConfig.PIN_WINDOW_N_INPUT_A,
            PinConfig.PIN_WINDOW_N_INPUT_B,
            "Window[North]",
            20,
            self.logger,
        )
        windows_group = WindowsGroup([window_se, window_n], self.logger)

        windows_group.close()
