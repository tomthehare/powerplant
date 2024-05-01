from pin_config import PinConfig


class WindowConfig:

    def __init__(
        self, open_duration: int, window_name: str, pin_1: int, pin_2: int
    ) -> None:
        self.movement_seconds: int = open_duration
        self.window_name: str = window_name
        self.pin_1: int = pin_1
        self.pin_2: int = pin_2


WINDOW_NORTH = "window_north"
WINDOW_EAST = "window_east"
WINDOW_SOUTH_EAST = "window_southeast"
WINDOW_SOUTH_WEST = "window_southwest"

WINDOWS_DICTIONARY = {
    WINDOW_NORTH: WindowConfig(
        31,
        "Window[North]",
        PinConfig.PIN_WINDOW_N_INPUT_A,
        PinConfig.PIN_WINDOW_N_INPUT_B,
    ),
    WINDOW_EAST: WindowConfig(
        10,
        "Window[North]",
        PinConfig.PIN_WINDOW_E_INPUT_A,
        PinConfig.PIN_WINDOW_E_INPUT_B,
    ),
    WINDOW_SOUTH_EAST: WindowConfig(
        12,
        "Window[SouthEast]",
        PinConfig.PIN_WINDOW_SE_INPUT_A,
        PinConfig.PIN_WINDOW_SE_INPUT_B,
    ),
    WINDOW_SOUTH_WEST: WindowConfig(
        12,
        "Window[SouthWest]",
        PinConfig.PIN_WINDOW_SW_INPUT_A,
        PinConfig.PIN_WINDOW_SW_INPUT_B,
    ),
}


def get_window_config(descriptor: str) -> WindowConfig:
    if descriptor not in WINDOWS_DICTIONARY:
        raise Exception("Window %s does not exist in configuration" % descriptor)

    return WINDOWS_DICTIONARY[descriptor]
