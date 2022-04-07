from flask import Flask, request, jsonify, render_template
from datetime import datetime
import time
import json
from json2html import *
from database.client import DatabaseClient
import pytz
from time_helper import format_timestamp_as_local, timestamp
from graph_helper import GraphHelper
import logging

app = Flask(__name__)
client = DatabaseClient("powerplant.db")
graph_helper = GraphHelper(client)
_logger = logging.getLogger(__name__)

def get_adjusted_offset_seconds():
    now = datetime.now(pytz.timezone('America/New_York'))
    return now.utcoffset().total_seconds()


@app.before_first_request
def ensure_db_exists():
    client.create_tables_if_not_exist()

def write_to_file(filename_prefix: str, data_string: str):
  dateTimeObj = datetime.now()
  dateStr = dateTimeObj.strftime("%Y-%m-%d")
    
  file = open("./gh_data/" + filename_prefix + dateStr + ".txt", "a")
  file.write(data_string + '\n')
  file.close()


@app.route('/')
def hello():
  return 'hey there fella ' + str(get_adjusted_offset_seconds())


@app.route('/scatter', methods=['GET'])
def scatter():
    date_start = round(time.time() - 86700)
    date_end = round(time.time())
    
    plot_object = graph_helper.get_temperature(date_start, date_end)

    return render_template(
        "scatter.html",
        date_start=format_timestamp_as_local(date_start),
        date_end=format_timestamp_as_local(date_end),
        plot1=plot_object
    )

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
  
  timestamp = float(pieces[1]) - get_adjusted_offset_seconds() 
  log_text = pieces[2]
 
  # write_to_file("logging_", data.get("data"))
  client.insert_log(timestamp, log_text)

  print(data.get("data"))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200

@app.route('/temp-humid-outside', methods = ['POST'])
def persist_temp_and_humid_outside(): 
  data = request.form

  pieces = data.get("data").split("|")
  
  unix_timestamp = float(pieces[1]) - get_adjusted_offset_seconds()
  humidity_string = pieces[2]
  temp_string = pieces[3]
  heat_index = pieces[4]

  humidity_pieces = humidity_string.split(":")
  humidity_value = humidity_pieces[1]

  temp_pieces = temp_string.split(":")
  temp_value = temp_pieces[1]

  heat_index_pieces = heat_index.split(":")
  heat_index_value = heat_index_pieces[1]

  dict_of_data = {"timestamp": format_timestamp_as_local(unix_timestamp), "humidity": humidity_value, "temp": temp_value, "heat-index": heat_index_value}

  # the_real_string = ','.join([str(unix_timestamp), humidity_value, temp_value, heat_index_value])
 
  # write_to_file("temp_humidity_", the_real_string)
  client.insert_outside_temperature(unix_timestamp, temp_value)
  client.insert_outside_humidity(unix_timestamp, humidity_value)
  client.insert_outside_heat_index(unix_timestamp, heat_index_value)

  print(json.dumps(dict_of_data, indent=4))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200


@app.route('/temp-humid-inside', methods = ['POST'])
def persist_temp_and_humid_inside(): 
  data = request.form

  pieces = data.get("data").split("|")
  
  unix_timestamp = float(pieces[1]) - get_adjusted_offset_seconds()
  humidity_string = pieces[2]
  temp_string = pieces[3]
  heat_index = pieces[4]

  humidity_pieces = humidity_string.split(":")
  humidity_value = humidity_pieces[1]

  temp_pieces = temp_string.split(":")
  temp_value = temp_pieces[1]

  heat_index_pieces = heat_index.split(":")
  heat_index_value = heat_index_pieces[1]

  dict_of_data = {"timestamp": format_timestamp_as_local(unix_timestamp), "humidity": humidity_value, "temp": temp_value, "heat-index": heat_index_value}

  # the_real_string = ','.join([str(unix_timestamp), humidity_value, temp_value, heat_index_value])
 
  # write_to_file("temp_humidity_", the_real_string)
  client.insert_inside_temperature(unix_timestamp, temp_value)
  client.insert_inside_humidity(unix_timestamp, humidity_value)
  client.insert_inside_heat_index(unix_timestamp, heat_index_value)

  print(json.dumps(dict_of_data, indent=4))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200

@app.route('/summary', methods = ['GET'])
def show_summary():
    now = round(time.time())
    inside_temps = client.read_inside_temperature(now - 300, now)
    inside_humids = client.read_inside_humidity(now - 300, now)
    inside_heat_indexes = client.read_inside_heat_index(now - 300, now)

    _logger.info('inside_temps: ' + json.dumps(inside_temps, indent=2))
    
    outside_temps = client.read_outside_temperature(now - 300, now)
    outside_humids = client.read_outside_humidity(now - 300, now)
    outside_heat_indexes = client.read_outside_heat_index(now - 300, now)

    output_dict = {}

    if len(outside_temps) == 0 or len(inside_temps) == 0:
        return 'error: no temperatures on file', 500
    
    inside_most_recent_temp = inside_temps[len(inside_temps)-1]
    inside_most_recent_humid = inside_humids[len(inside_humids)-1]
    inside_most_recent_heat_index = inside_heat_indexes[len(inside_heat_indexes)-1]

    outside_most_recent_temp = outside_temps[len(outside_temps)-1]
    outside_most_recent_humid = outside_humids[len(outside_humids)-1]
    outside_most_recent_heat_index = outside_heat_indexes[len(outside_heat_indexes)-1]

    output_dict['inside-temperature'] = {'Time': format_timestamp_as_local(inside_most_recent_temp[0]), 'InsideDegreesF': inside_most_recent_temp[1]}
    output_dict['inside-humidity'] = {'Time': format_timestamp_as_local(inside_most_recent_humid[0]), 'InsidePercentage': inside_most_recent_humid[1]}
    output_dict['inside-heat-index'] = {'Time': format_timestamp_as_local(inside_most_recent_heat_index[0]), 'InsideDegreesF-HI': inside_most_recent_heat_index[1]}

    output_dict['outside-temperature'] = {'Time': format_timestamp_as_local(outside_most_recent_temp[0]), 'OutsideDegreesF': outside_most_recent_temp[1]}
    output_dict['outside-humidity'] = {'Time': format_timestamp_as_local(outside_most_recent_humid[0]), 'OutsidePercentage': outside_most_recent_humid[1]}
    output_dict['outside-heat-index'] = {'Time': format_timestamp_as_local(outside_most_recent_heat_index[0]), 'OutsideDegreesF-HI': outside_most_recent_heat_index[1]}

    json_dict = json.dumps(output_dict)

    output = json2html.convert(json_dict)

    return output, 200


@app.route('/record-soil-conductivity', methods = ['POST'])
def record_soil_conductivity():
    data = request.form

    pieces = data.get('data').split('|')
    
    unix_timestamp = float(pieces[1]) - get_adjusted_offset_seconds()
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

