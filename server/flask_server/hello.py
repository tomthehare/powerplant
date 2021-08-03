from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello():
	return 'hey there fella'

@app.route('/temp-humid', methods = ['POST'])
def persist_temp_and_humid(): 
  data = request.form

  dateTimeObj = datetime.now()
  dateStr = dateTimeObj.strftime("%d-%b-%Y")

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

  file = open("./gh_data/temp_humidity_" + dateStr + ".txt", "a")
  file.write(the_real_string + '\n')
  file.close()

  print(dict_of_data)

  return jsonify(isError=False, message="Success", statusCode=200), 200