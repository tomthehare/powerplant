import json


class ValveConfig:
    def __init__(self, id):
        self.id = id
        self.description = "UNKNOWN"
        self.conductivity_threshold = 1.0
        self.watering_delay_seconds = 1
        self.open_duration_seconds = 1
        self.pump_modulation_half_cycle_seconds = 2

    def __str__(self):
        return json.dumps(
            {
                "id": self.id,
                "description": self.description,
                "conductivity_threshold": self.conductivity_threshold,
                "watering_delay_seconds": self.watering_delay_seconds,
                "open_duration_seconds": self.open_duration_seconds,
                "pump_modulation_half_cycle_seconds": self.pump_modulation_half_cycle_seconds,
            },
            indent=2,
        )
