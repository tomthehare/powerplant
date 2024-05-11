from dtos.valve_config import ValveConfig


class Config:
    def __init__(self):
        self.valves = {}
        self.fan_temp = 85
        self.water_every_days = 1
        self.water_at_hours = [7]

    def update_water_config(self, water_config):
        self.water_every_days = water_config["water_every_days"]
        self.water_at_hours = [int(a) for a in water_config["hours"]]

    def update_fan_temp_config(self, fan_temp):
        if isinstance(fan_temp, dict):
            fan_temp = fan_temp["fan_temperature"]

        self.fan_temp = int(fan_temp)

    def update_valve_config(self, input_config: list):
        for valve_config in input_config:
            valve_id = valve_config["valve_id"]
            if valve_id not in self.valves.keys():
                self.valves[valve_id] = ValveConfig(valve_id)

            self.valves[valve_id].description = valve_config["description"]

            self.valves[valve_id].open_duration_seconds = valve_config[
                "open_duration_seconds"
            ]

    def get_valve_config(self, valve_id):
        if valve_id not in self.valves.keys():
            return ValveConfig(valve_id)

        return self.valves[valve_id]
