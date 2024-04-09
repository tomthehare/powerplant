from fastapi import FastAPI, Request

from database.client import DatabaseClient
from payload_builder import PayloadBuilder
from models.weather_sample import WeatherSample
from utilities.validator import Validator
from utilities.time_helper import TimeHelper
from utilities.power_plant_logger import PowerPlantLogger

app = FastAPI()
db_client = DatabaseClient('powerplant.db')
db_client.create_tables_if_not_exist()

logger = PowerPlantLogger.get_logger()

payload_builder = PayloadBuilder(logger, db_client)

"""
What are our entities?

WeatherSample
Config
    -> Fan Temp
    -> Watering Schedule
    -> Valves
WateringQueue
    -> PUT (push), DELETE (dequeue)
Valves
Events

"""

@app.get("/")
def read_root():
    return {"power": "PLANT"}


@app.get("/temperature-samples")
def get_weather_samples(location: str, hours_back: int = 8):
    ts_start = TimeHelper.timestamp() - (3600 * hours_back)
    ts_end = TimeHelper.timestamp()

    return payload_builder.get_temperature_samples(location, ts_start, ts_end)

@app.get("/humidity-samples")
def get_weather_samples(location: str, hours_back: int = 8):
    ts_start = TimeHelper.timestamp() - (3600 * hours_back)
    ts_end = TimeHelper.timestamp()

    logger.info("range: %s -> %s", str(ts_start), str(ts_end))

    return payload_builder.get_humidity_samples(location, ts_start, ts_end)

@app.post("/weather-samples")
def post_weather_sample(sample: WeatherSample):
    Validator.validate_location(sample.location)

    if sample.location == "inside":
        db_client.insert_inside_humidity(sample.timestamp, sample.humidity)
        db_client.insert_inside_temperature(sample.timestamp, sample.temperature)
    else:
        db_client.insert_outside_humidity(sample.timestamp, sample.humidity)
        db_client.insert_outside_temperature(sample.timestamp, sample.temperature)

@app.get("/config")
def get_config():
    pass

@app.get("/watering-queue")
def get_watering_queue():
    """
    Get the current watering queue
    """
    pass

@app.put("/watering-queue")
def put_watering_queue():
    """
    Adds a new water request to the end of the watering queue
    """
    pass

@app.delete("/watering-queue")
def delete_watering_queue():
    """
    Dequeues from the front of the queue
    """
    pass

@app.put("/valves/{valve_id}")
def open_valve():
    """
    Put in this case opens the valve
    """
    pass

@app.delete("/valves/{valve_id}")
def close_valve():
    """
    Delete in this case closes the valve
    """
    pass

@app.delete("/valves")
def close_all_valves():
    """
    Ensure all valves are closed
    """
    pass

@app.get("/events")
def get_events(type: str = ""):
    """
    Get all events with a specific type as a query param
    """
    pass

@app.post("/events")
def create_event():
    """
    Create a new event
    """
    pass

