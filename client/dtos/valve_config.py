class ValveConfig:
    def __init__(self, id):
        self.id = id
        self.description = "UNKNOWN"
        self.conductivity_threshold = 1.0
        self.watering_delay_seconds = 1
        self.open_duration_seconds = 1
        self.pump_modulation_half_cycle_seconds = 2
