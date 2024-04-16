from bootstrap import Bootstrap
from clients.config_client import ConfigClient
from clients.water_queue_client import WaterQueueClient
from models.config import Config
from models.event import Event
from models.water_queue_entry import WaterQueueEntry
from models.weather_sample import WeatherSample
from utilities.validator import Validator
from utilities.time_helper import TimeHelper

bootstrapper = Bootstrap()
bootstrapper.bootstrap_app()

payload_builder = bootstrapper.payload_builder
db_client = bootstrapper.db_client
logger = bootstrapper.logger
app = bootstrapper.app

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
def get_temperature_samples(location: str, hours_back: int = 8):
    ts_start = TimeHelper.timestamp() - (3600 * hours_back)
    ts_end = TimeHelper.timestamp()

    return payload_builder.get_temperature_samples(location, ts_start, ts_end)

@app.get("/humidity-samples")
def get_humidity_samples(location: str, hours_back: int = 8):
    ts_start = TimeHelper.timestamp() - (3600 * hours_back)
    ts_end = TimeHelper.timestamp()

    logger.info("range: %s -> %s", str(ts_start), str(ts_end))

    return payload_builder.get_humidity_samples(location, ts_start, ts_end)

@app.get('/weather-samples')
def get_weather_samples(location: str, hours_back: int = 8):
    temp_samples = get_temperature_samples(location, hours_back)
    humid_samples = get_humidity_samples(location, hours_back)

    # Now we must combine them into a single payload to make rendering on the front end easier
    w_samples = {}
    for t_sample in temp_samples:
        timestamp = t_sample['timestamp']
        w_samples[timestamp] = {
            'timestamp': timestamp,
            'temperature': t_sample['temperature'],
            'humidity': None
        }

    for h_sample in humid_samples:
        timestamp = h_sample['timestamp']
        if timestamp in w_samples:
            w_samples[timestamp]['humidity'] = h_sample['humidity']

    return [w_samples[a] for a in w_samples]

@app.post("/weather-samples", status_code=201)
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
    return ConfigClient(logger).get_config()

@app.patch("/config")
def patch_config(config: Config):
    ConfigClient(logger).set_config(config)

@app.get("/watering-queue")
def get_watering_queue():
    """
    Get the current watering queue
    """
    return WaterQueueClient().get_queue()

@app.put("/watering-queue")
def put_watering_queue(entry: WaterQueueEntry):
    """
    Adds a new water request to the end of the watering queue
    """
    WaterQueueClient().enqueue_entry(entry)

@app.delete("/watering-queue")
def delete_watering_queue():
    """
    Dequeues from the front of the queue
    """
    WaterQueueClient().dequeue_entry()

@app.get("/events")
def get_events(type: str = ""):
    """
    Get all events with a specific type as a query param
    """
    return payload_builder.get_events(type)

@app.post("/events", status_code=201)
def create_event(event: Event):
    """
    Create a new event
    """
    db_client.insert_powerplant_event(event.event_id, event.subject_type, event.subject_id, event.verb, event.timestamp)

@app.get('/fan-activity')
def fan_activity(hours_back: int = 24):
    # todo - method to help distill down the events so the node code doesn't have to do it.
    pass

@app.get('/plant-groups')
def get_plant_groups():
    config_client = ConfigClient(logger)
    config = config_client.get_config()

    # For each plant group, attempt to find the last time the valve was closed (or opened)
    events = db_client.get_powerplant_events(0, 2147483647) # All events for all time!

    valve_events = [a for a in events if a['subject_type'] == 'valve']

    return_data = []
    for plant_group in config.plant_groups:
        valve_id = int(plant_group.valve_id)
        description = plant_group.description
        last_watered = None

        for valve_event in valve_events:
            if int(valve_event['subject_id']) != valve_id:
                continue

            if not last_watered or last_watered < valve_event['timestamp']:
                last_watered = valve_event['timestamp']

        return_data.append(
            {
                'valve_id': valve_id,
                'description': description,
                'last_watered': last_watered
            }
        )

    return return_data


