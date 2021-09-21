import random
from database.client import DatabaseClient

client = DatabaseClient("mock_db.db")

client.create_tables_if_not_exist()

client.insert_temperature(random.randint(0, 100000), 22.2)
client.insert_humidity(random.randint(0, 100000), 91.57)
client.insert_cpu_temperature(random.randint(0, 100000), 88)
client.insert_valve_operation(random.randint(0, 100000), 1, 1)
client.insert_valve_operation(random.randint(0, 100000), 1, 2)
client.insert_heat_index(random.randint(0,1000000), 200)
client.insert_log(2002, "no bad words")

print(client.read_temperature(0, 9999999))
print(client.read_humidity(0, 9999999))
print(client.read_heat_index(0, 9999999))
print(client.read_logs(0, 9999999))
