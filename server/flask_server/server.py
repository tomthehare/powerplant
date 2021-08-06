from flask import Flask, request, jsonify
from datetime import datetime
import time
import json

app = Flask(__name__)

def write_to_file(filename_prefix: str, data_string: str):
  dateTimeObj = datetime.now()
  dateStr = dateTimeObj.strftime("%Y-%m-%d")
    
  file = open("./gh_data/" + filename_prefix + dateStr + ".txt", "a")
  file.write(data_string + '\n')
  file.close()


@app.route('/')
def hello():
  return 'hey there fella'


@app.route('/cpu-temp', methods = ['POST'])
def cpu_temp():  
  data = request.form

  print(data.get("data"))

  pieces = data.get("data").split("|")

  temp_c = pieces[0].split(":")[1]
  temp_f = pieces[1].split(":")[1]

  string_to_write = ",".join([str(round(time.time())), temp_c, temp_f])  

  write_to_file("cpu_temp_", string_to_write)
    
  return jsonify(isError=False, message="Success", statusCode=200), 200

@app.route('/temp-humid', methods = ['POST'])
def persist_temp_and_humid(): 
  data = request.form

  pieces = data.get("data").split("|")
  unix_timestamp = pieces[0]
  humidity_string = pieces[1]
  temp_string = pieces[2]
  heat_index = pieces[3]

  humidity_pieces = humidity_string.split(":")
  humidity_value = humidity_pieces[1]

  temp_pieces = temp_string.split(":")
  temp_value = temp_pieces[1]

  heat_index_pieces = heat_index.split(":")
  heat_index_value = heat_index_pieces[1]

  dict_of_data = {"humidity": humidity_value, "temp": temp_value, "heat-index": heat_index_value}

  the_real_string = ','.join([unix_timestamp, humidity_value, temp_value, heat_index_value])
 
  write_to_file("temp_humidity_", the_real_string) 

  print(json.dumps(dict_of_data, indent=4))
    
  return jsonify(isError=False, message="Success", statusCode=200), 200
