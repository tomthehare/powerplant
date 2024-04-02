from logging import Logger
import Adafruit_DHT
from client.components.time_observer import TimeObserver
from client.dtos.temp_humid_reading import TempHumidReading

DHT_SENSOR = Adafruit_DHT.DHT22


class TempHumidSensor:
    def __init__(self, pin: int, logger: Logger, time_observer: TimeObserver = None):
        logger.info("Setting up temperature/humidity sensor on data pin %d", pin)
        self.data_pin = pin
        self.last_read_ts = 0
        self.last_reading = None
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

    def read(self):
        if (self.last_read_ts + 2) >= self.time_observer.timestamp():
            self.logger.info("Too soon to read temp/humid on pin %d" % self.data_pin)
            return

        self.last_read_ts = self.time_observer.timestamp()

        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, self.data_pin)
        self.logger.debug(
            "Read temp and humidity on pin %d: %f *F, %f percent Humidity",
            self.data_pin,
            temperature,
            humidity,
        )

        if humidity is not None and temperature is not None:
            self.last_reading = TempHumidReading(temperature, humidity)
            return self.last_reading
        else:
            self.logger.error("Unable to read temp/humidity on pin %d", self.data_pin)
            raise Exception("Unable to read sensor")

    def get_last_reading(self):
        return self.last_reading
