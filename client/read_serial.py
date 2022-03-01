import serial
import time
import requests
import pytz
import datetime

ser = None;

def get_adjusted_offset_seconds():
    now = datetime.datetime.now(pytz.timezone('America/New_York'))
    return now.utcoffset().total_seconds()

while (True):
    try:
        ser = serial.Serial('/dev/ttyACM0')
        break

    except Exception as ex:
        print("No serial, will try again soon.")
        print(ex)
        time.sleep(5)


while (True):
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")

    if decoded_bytes == "time-please":
        print("Negotiating time with arduino...")
        current_time_adjusted = round(time.time()) + get_adjusted_offset_seconds()

        print("It is " + str(current_time_adjusted))
        ser.write(bytes(str(current_time_adjusted) + '>', 'ascii'))
    else:
        file_payload = decoded_bytes

        print(file_payload)

        payload_parts = file_payload.split("|")
        payload_identifier = payload_parts[0]

        if payload_identifier == "&sm":
            try:
              r = requests.post('http://192.168.86.182:5000/record-soil-conductivity', data ={'data': file_payload})
            except:
              print('error pushing request to soil conductivity endpoint')
        elif payload_identifier == "&log":
            try:
                r = requests.post('http://192.168.86.182:5000/logging', data ={'data': file_payload})
            except:
                print('error pushing request to logging endpoint')
        else:
            print('hmm no idea what to do with that request!')
