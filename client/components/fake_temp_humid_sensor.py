from logging import Logger
from components.temp_humid_sensor import TempHumidSensor
from components.time_observer import TimeObserver
from dtos.temp_humid_reading import TempHumidReading


class FakeTempHumidSensor(TempHumidSensor):
    def __init__(
        self,
        pin: int,
        logger: Logger,
        location: str,
        time_observer: TimeObserver = None,
    ):
        super().__init__(pin, logger, location, time_observer)
        self.is_on: bool = False

    def read(self):
        pass

    def get_last_reading(self):
        if self.is_on:
            self.is_on = False
            return TempHumidReading(20, 94)  # celcius!
        else:
            self.is_on = True
            return TempHumidReading(40, 94)  # celcius!
        #
