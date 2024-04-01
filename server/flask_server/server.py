from flask import Flask, request, jsonify, render_template, render_template_string, Response
from datetime import datetime
import time
import json
from json2html import *
from database.client import DatabaseClient
import pytz
from time_helper import format_timestamp_as_local, timestamp, format_delta
from graph_helper import GraphHelper
import logging
import os.path
import math

app = Flask(__name__)
client = DatabaseClient("powerplant.db")
db_client = client
graph_helper = GraphHelper(client)

_logger = logging.getLogger('powerplant')
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logFormatter)
_logger.setLevel(logging.DEBUG)
_logger.addHandler(handler)


def get_adjusted_offset_seconds():
    now = datetime.now(pytz.timezone('America/New_York'))
    return now.utcoffset().total_seconds()


@app.before_first_request
def ensure_db_exists():
    client.create_tables_if_not_exist()


@app.route('/')
def hello():
    _logger.info('Hey there!')
    return 'hey there fella ' + str(get_adjusted_offset_seconds())

@app.route('/cpu-temp', methods = ['POST'])
def cpu_temp():  
  data = request.form

  print(data.get("data"))

  pieces = data.get("data").split("|")

  temp_c = pieces[0].split(":")[1]
  temp_f = pieces[1].split(":")[1]

  string_to_write = ",".join([str(), temp_c, temp_f])  

  # write_to_file("cpu_temp_", string_to_write)
  client.insert_cpu_temperature(round(time.time()), temp_f)
    
  return jsonify(isError=False, message="Success", statusCode=200), 200

@app.route('/logging', methods = ['POST'])
def logging():
  data = request.form

  pieces = data.get("data").split("|")
  
  print(str(pieces))
  
  timestamp = float(pieces[1])
  log_text = pieces[2]
 
  # write_to_file("logging_", data.get("data"))
  client.insert_log(timestamp, log_text)

  print(data.get("data"))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200


def parse_humid_temp(data):
  pieces = data.get("data").split("|")
  
  unix_timestamp = float(pieces[1])
  humidity_string = pieces[2]
  temp_string = pieces[3]
  heat_index = pieces[4]

  humidity_pieces = humidity_string.split(":")
  humidity_value = humidity_pieces[1]

  temp_pieces = temp_string.split(":")
  temp_value = temp_pieces[1]

  heat_index_pieces = heat_index.split(":")
  heat_index_value = heat_index_pieces[1]

  return (unix_timestamp, temp_value, humidity_value, heat_index_value)

def get_valve_config_dict():
    database_client = DatabaseClient('powerplant.db')
    return database_client.get_valve_config()

@app.route('/valve-config', methods = ['GET'])
def get_valve_config():
    valve_config = get_valve_config_dict()
    return jsonify(valve_config), 200

def read_fan_config():
    fan_config_path = 'fan-config.json'

    with open(fan_config_path, 'r') as f:
        config = json.load(f)

    return config

@app.route('/fan-config', methods=['GET'])
def get_fan_config():
    config = read_fan_config()
    return jsonify(config), 200


@app.route('/fan-config/temp', methods=['POST'])
def set_fan_temp():
    config = read_fan_config()

    if 'fan_temp' not in request.form:
        return 'Missing fan temp in body', 400

    config['fan_temp'] = request.form['fan_temp']

    with open('fan-config.json', 'w') as f:
        json.dump(config, f)

    return 'Set new temp', 200

def get_watering_queue_data():
    file_path = 'watering_queue.json'

    queue = []

    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r') as f:
        queue = json.load(f)

    return queue


@app.route('/valves/watering-queue', methods=['GET'])
def get_valve_watering_queue():
    queue_data = get_watering_queue_data()

    return Response(json.dumps(queue_data), mimetype='application/json', status=200)

def water_some_stuff(valve_ids):
    queue_data = get_watering_queue_data()

    data = request.form

    if 'open_duration_seconds' in data:
        open_duration = data['open_duration_seconds']
    else:
        _logger.info('Defaulting open duration seconds to 60 as it was not passed in.')
        open_duration = 60

    for valve_id in valve_ids:
        queue_entry = {'valve_id': valve_id, 'open_duration_seconds': open_duration}
        queue_data.append(queue_entry)

    with open('watering_queue.json', 'w') as f:
        json.dump(queue_data, f)

    return json.dumps(queue_data), 201

@app.route('/valves/<valve_id>/water', methods=['POST'])
def add_valve_queue(valve_id):
    queue_data = get_watering_queue_data()

    for entry in queue_data:
        queue_valve_id = entry['valve_id']
        if queue_valve_id == valve_id:
            return 'Valve already in queue', 400

    return water_some_stuff([valve_id])

@app.route('/valves/water_tomatoes', methods=['POST'])
def water_tomatoes():
    return water_some_stuff([7,8,9])


@app.route('/valves/water', methods=['POST'])
def water_all():
    valve_config = db_client.get_valve_config()
    return water_some_stuff([a['valve_id'] for a in valve_config])

@app.route('/valves/watering-queue/<valve_id>', methods=['DELETE'])
def remove_watering_queue(valve_id):
    queue_data = get_watering_queue_data()

    for entry in queue_data:
        queue_valve_id = entry['valve_id']
        if int(queue_valve_id) == int(valve_id):
            queue_data.remove(entry)
            break

    with open('watering_queue.json', 'w') as f:
        json.dump(queue_data, f)
    
    return 'Removed', 200

@app.route('/temp-humid-outside', methods = ['POST'])
def persist_temp_and_humid_outside():
  (unix_timestamp, temp_value, humidity_value, heat_index_value) = parse_humid_temp(request.form)

  dict_of_data = {"timestamp": format_timestamp_as_local(unix_timestamp), "humidity": humidity_value, "temp": temp_value, "heat-index": heat_index_value}

  client.insert_outside_temperature(unix_timestamp, temp_value)
  client.insert_outside_humidity(unix_timestamp, humidity_value)
  client.insert_outside_heat_index(unix_timestamp, heat_index_value)

  print(json.dumps(dict_of_data, indent=4))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200


@app.route('/temp-humid-inside', methods = ['POST'])
def persist_temp_and_humid_inside(): 
  (unix_timestamp, temp_value, humidity_value, heat_index_value) = parse_humid_temp(request.form)

  dict_of_data = {"timestamp": format_timestamp_as_local(unix_timestamp), "humidity": humidity_value, "temp": temp_value, "heat-index": heat_index_value}

  client.insert_inside_temperature(unix_timestamp, temp_value)
  client.insert_inside_humidity(unix_timestamp, humidity_value)
  client.insert_inside_heat_index(unix_timestamp, heat_index_value)

  print(json.dumps(dict_of_data, indent=4))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200


def get_summary_dictionary():
    now = round(time.time())
    inside_temps = client.read_inside_temperature(now - 360, now)
    inside_humids = client.read_inside_humidity(now - 360, now)

    outside_temps = client.read_outside_temperature(now - 360, now)
    outside_humids = client.read_outside_humidity(now - 360, now)

    output_dict = {
        'Inside Temperature': {'Time': 0, 'InsideDegreesF': 0},
        'Inside Humidity': {'Time': 0, 'InsidePercentage': 0},
        'Outside Temperature': {'Time': 0, 'OutsideDegreesF': 0},
        'Outside Humidity': {'Time': 0, 'OutsidePercentage': 0}
    }

    if len(inside_temps) > 0:
        inside_most_recent_temp = inside_temps[len(inside_temps)-1]
        output_dict['Inside Temperature'] = {
            'Time': format_timestamp_as_local(inside_most_recent_temp[0]), 
            'InsideDegreesF': inside_most_recent_temp[1]
        }

    if len(inside_humids) > 0:
        inside_most_recent_humid = inside_humids[len(inside_humids)-1]
        output_dict['Inside Humidity'] = {
            'Time': format_timestamp_as_local(inside_most_recent_humid[0]), 
            'InsidePercentage': inside_most_recent_humid[1]
        }

    if len(outside_temps) > 0:
        outside_most_recent_temp = outside_temps[len(outside_temps)-1]
        output_dict['Outside Temperature'] = {
            'Time': format_timestamp_as_local(outside_most_recent_temp[0]), 
            'OutsideDegreesF': outside_most_recent_temp[1]
        }

    if len(outside_humids) > 0:
        outside_most_recent_humid = outside_humids[len(outside_humids)-1]
        output_dict['Outside Humidity'] = {
            'Time': format_timestamp_as_local(outside_most_recent_humid[0]), 
            'OutsidePercentage': outside_most_recent_humid[1]
        }

    return output_dict

@app.route('/summary', methods = ['GET'])
def show_summary():
    data = get_summary_dictionary()
    json_string = json.dumps(data)

    if not json_string:
        return 'error: no temperatures on file', 500

    output = json2html.convert(json_string)

    return output, 200

def get_watering_queue_detailed():
    watering_queue = get_watering_queue_data()
    valve_config_dict = get_valve_config_dict()

    detailed_queue = []
    for entry in watering_queue:
        valve_config_entry = {'description': 'Unknown'}
        for config_entry in valve_config_dict:
            if int(config_entry['valve_id']) == int(entry['valve_id']):
                valve_config_entry = config_entry
                break

        detailed_queue.append(
            {
                'valve_id': entry['valve_id'],
                'valve_description': valve_config_entry['description'],
                'open_duration_seconds': entry['open_duration_seconds']
            }
        )

    return detailed_queue

def get_valve_description(valve_id):
    valve_config_list = get_valve_config_dict()

    for config_entry in valve_config_list:
        if int(config_entry['valve_id']) == int(valve_id):
            return valve_config_entry['description']

    return 'Unknown'

@app.route('/scatter', methods=['GET'])
def scatter():
    hours_back = request.args.get("hours_back", default=24, type=int)

    date_start = round(time.time() - (3600 * hours_back))
    date_end = round(time.time())
    
    temp_plot_object = graph_helper.get_temperature_graph_object(date_start, date_end)
    humid_plot_object = graph_helper.get_humidity_graph_object(date_start, date_end)

    summary_details = get_summary_dictionary()

    _logger.info(json.dumps(summary_details, indent=2))

    if not summary_details:
        inside_temperature = -1
        outside_temperature = -1
        inside_humidity = -1
        outside_humidity = -1
    else:
        inside_temperature = summary_details['Inside Temperature']['InsideDegreesF']
        outside_temperature = summary_details['Outside Temperature']['OutsideDegreesF']
        inside_humidity = summary_details['Inside Humidity']['InsidePercentage']
        outside_humidity = summary_details['Outside Humidity']['OutsidePercentage']

    fan_config = read_fan_config()
    watering_queue = get_watering_queue_detailed()
    valve_config = get_valve_config_dict()

    valve_history = {}
    for valve_dict in valve_config:
        valve_id = valve_dict['valve_id']
        last_valve_event = db_client.get_last_valve_event(valve_id)
        print(last_valve_event)
        valve_history[valve_id] = last_valve_event
        closed_ts = valve_history[valve_id]['closed']
        if not closed_ts:
            closed_ts = timestamp()
        valve_history[valve_id]['delta_closed'] = format_delta(timestamp() - closed_ts)

    print(valve_history)

    fan_data_object = graph_helper.get_fan_data(date_start, date_end, 3600)
    fan_on_off_data = client.read_fan_data(date_start, date_end)

    fan_events = []
    for event_hash, ts_on, ts_off in fan_on_off_data:
        if ts_off is None:
            ts_off = round(time.time())

        minutes_on_total = round(((ts_off-ts_on) / 60))
        
        hours_on = math.floor(minutes_on_total / 60)
        minutes_remainder = minutes_on_total % 60

        human_time_string = ""
        if hours_on > 0:
            human_time_string = "%d hours " % hours_on

        human_time_string = human_time_string + ("%d minutes" % minutes_remainder)

        fan_events.append(
            {
                'ts_on': format_timestamp_as_local(ts_on), 
                'ts_off': format_timestamp_as_local(ts_off),
                'on_minutes': human_time_string
            }
        )

    fan_events.reverse()

    return render_template(
        "scatter.html",
        date_start=format_timestamp_as_local(date_start),
        date_end=format_timestamp_as_local(date_end),
        temp_plot=temp_plot_object,
        humid_plot=humid_plot_object,
        inside_temp=inside_temperature,
        outside_temp=outside_temperature,
        delta_temp=round(inside_temperature - outside_temperature, 1),
        inside_humidity=inside_humidity,
        outside_humidity=outside_humidity,
        delta_humidity=round(inside_humidity - outside_humidity, 1),
        fan_temp=fan_config['fan_temp'],
        watering_queue=watering_queue,
        valve_config_list=valve_config,
        fan_data_object=fan_data_object,
        fan_events=fan_events,
        valve_history=valve_history
    )

@app.route('/record-soil-conductivity', methods = ['POST'])
def record_soil_conductivity():
    data = request.form

    pieces = data.get('data').split('|')
    
    unix_timestamp = float(pieces[1])
    plant_tag = pieces[2]
    soil_voltage_reading = pieces[3]

    dict_of_data = {"timestamp": format_timestamp_as_local(unix_timestamp), "plant-tag": plant_tag, "soil-voltage": soil_voltage_reading}

    client.insert_soil_voltage(unix_timestamp, plant_tag, soil_voltage_reading)

    print(json.dumps(dict_of_data, indent=4))
    
    return jsonify(isError=False, message="Success", statusCode=200), 200

@app.route('/plant-group-thirst/{descriptor}', methods=['GET'])
def get_plant_group_thirst(descriptor):
    needs_water = False

    # Get plant group details
    thirst_threshold, last_reading, last_water_timestamp = client.get_plant_group_details(descriptor)

    # If its been over three hours and is reporting being hungry
    if last_reading > thirst_threshold and (time_helper.timestamp() - last_water_timestamp) > (60 * 60 * 3):
        needs_water = True

    return  jsonify({'needs_water': needs_water}), 200

@app.route('/events', methods=['POST'])
def log_fan_event():
    event_data = request.form
    json_event_data = json.dumps(event_data, indent=2)

    subject = event_data['subject']
    time = event_data['time']
    event = event_data['event']
    sync_hash = event_data['sync_hash']

    if subject == 'fan':
        if event == 'turned_on':
            if db_client.fan_event_exists(sync_hash):
                _logger.warning('event was already in database: %s' % json_event_data)
            else:
                db_client.insert_fan_on_event(time, sync_hash)
                _logger.info('processed event: %s' % json_event_data)
        elif event == 'turned_off' or event == 'turned off':
            if db_client.fan_event_exists(sync_hash):
                db_client.update_fan_off_event(time, sync_hash)
                _logger.info('processed_event: %s' % json_event_data)
            else:
                _logger.warning('event not in db for off event: %s' % json.dumps(event_data, indent=2))
    elif subject.startswith('valve_'):
        valve_id = int(subject.replace('valve_', ''))

        if event == 'opened':
            if db_client.valve_event_exists(sync_hash):
                _logger.warning('event was already in database: %s' % json_event_data)
            else:
                db_client.insert_valve_open_event(valve_id, time, sync_hash)
                _logger.info('processed event: %s' % json_event_data)
        elif event == 'closed':
            if db_client.valve_event_exists(sync_hash):
                db_client.update_valve_close_event(time, sync_hash)
                _logger.info('processed_event: %s' % json_event_data)
            else:
                _logger.warning('event not in db for valve closed event: %s' % json.dumps(event_data, indent=2))

    else:
        _logger.warning('got event we didnt recognize: %s' % json.dumps(event_data, indent=2))

    return 'processed', 200
