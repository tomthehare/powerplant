from logging import Logger

from database.client import DatabaseClient
from utilities.validator import Validator


class PayloadBuilder:
    def __init__(self, logger: Logger, database_client: DatabaseClient):
        self.logger = logger
        self.database_client = database_client

    def get_temperature_samples(self, location: str, min_seconds: int, max_seconds: int):
        Validator.validate_location(location)

        if location == "inside":
            samples = self.database_client.read_inside_temperature(min_seconds, max_seconds)
        else:
            samples = self.database_client.read_outside_temperature(min_seconds, max_seconds)

        return [{"timestamp": a[0], "temperature": a[1]} for a in samples]

    def get_humidity_samples(self, location: str, min_seconds: int, max_seconds: int):
        Validator.validate_location(location)

        if location == "inside":
            samples = self.database_client.read_inside_humidity(min_seconds, max_seconds)
        else:
            samples = self.database_client.read_outside_humidity(min_seconds, max_seconds)

        return [{"timestamp": a[0], "humidity": a[1]} for a in samples]

