from gpiozero import CPUTemperature
import requests

cpu = CPUTemperature()
temp_c = cpu.temperature
temp_f = temp_c * (9/5) + 32

# Push to server

file_payload = 'temp_c:' + str(temp_c) + '|temp_f:' + str(temp_f)

try:
    response = requests.post('http://192.168.86.182:5000/cpu-temp', data = {'data': file_payload})
except Exception as e:
    print('Failed to upload to server: ' + str(e))
