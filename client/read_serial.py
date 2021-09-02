import serial
import time
import requests

ser = serial.Serial('/dev/ttyACM0')
    
while (True):
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")

    if decoded_bytes == "time-please":
        print("Negotiating time with arduino...")
        current_time_adjusted = round(time.time()) - 14400;
        
        print("It is " + str(current_time_adjusted))
        ser.write(bytes(str(current_time_adjusted) + '>', 'ascii'))
    else:
        file_payload = decoded_bytes

        print(file_payload)
        
        payload_parts = file_payload.split("|")
        payload_identifier = payload_parts[1]

        if payload_identifier == "&th":
            try:
                print("sending request")
                #r = requests.post('http://192.168.86.182:5000/temp-humid', data ={'data': file_payload})
                #print(r.json())
            except:
                print('error pushing request to temp-humid endpoint')
