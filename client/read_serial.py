import serial
import time
import requests

ser = serial.Serial('/dev/ttyACM0')
while (True):
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
            
    file_payload = str(round(time.time())) + '|' + decoded_bytes    
    
    print(file_payload)
    
    #file1 = open("/home/pi/gh_data/temp_humidity.txt", "a")  # append mode
    #file1.write(file_payload + '\n')
    #file1.close()

    # Push to our server!!
    try:
        r = requests.post('http://192.168.86.176:5000/temp-humid', data ={'data': file_payload})
        print(r.json())
    except:
        print('error pushing request')