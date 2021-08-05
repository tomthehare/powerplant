import serial
import time
import requests

ser = serial.Serial('/dev/ttyACM0')

ser_bytes = ser.readline()
decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")

file_payload = str(round(time.time())) + '|' + decoded_bytes

# Push to our server!!
try:
    r = requests.post('http://192.168.86.182:5000/temp-humid', data ={'data': file_payload})
    print(r.json())
except:
    print('error pushing request')
