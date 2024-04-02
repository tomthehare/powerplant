from client.components.time_observer import TimeObserver
from heat_index import calculate as heatindex
import json


# TODO: this is actually probably 2 classes - the thing doing the reading and then the data class that is the values
class TempHumidReading:
    def __init__(self, temp, humid, time_observer: TimeObserver = None):
        self.temp_c = temp
        self.humid = humid
        self.read_at_ts = (time_observer or TimeObserver()).timestamp()

    def get_temp(self):
        return round((9 * self.temp_c) / 5 + 32, 1)

    def get_temperature(self):
        return self.get_temp()

    def get_humidity(self):
        return round(self.humid, 1)

    def get_heat_index(self):
        return round(heatindex.from_fahrenheit(self.get_temp(), self.get_humidity()), 1)

    def __str__(self):
        self.to_string()

    def to_string(self):
        return json.dumps(
            {"temperature": self.get_temperature(), "humidity": self.get_humidity()},
            indent=2,
        )
