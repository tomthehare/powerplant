from components.pump import Pump
from components.time_observer import TimeObserver


class PumpModulationTask(Pump):

    def __init__(
        self,
        pump: Pump,
        half_cycle_time_seconds_default: int = 2,
        time_observer: TimeObserver = None,
    ) -> None:
        self.pump = pump
        self.pump_should_be_on: bool = False
        self.half_cycle_time_seconds = half_cycle_time_seconds_default
        self.half_cycle_time_seconds_override = None
        self.time_observer = time_observer or TimeObserver()
        self._last_half_cycle_timestamp = self.time_observer.timestamp()

    def turn_on(self, pump_cycle_time_seconds_override: int = None):
        self.half_cycle_time_seconds_override = pump_cycle_time_seconds_override
        self.pump_should_be_on = True
        self._internal_turn_on()

    def turn_off(self):
        self.half_cycle_time_seconds_override = None
        self.pump_should_be_on = False
        self._internal_turn_off()

    def _internal_turn_off(self):
        self.pump.turn_off()
        self._last_half_cycle_timestamp = self.time_observer.timestamp()

    def _internal_turn_on(self):
        self.pump.turn_on()
        self._last_half_cycle_timestamp = self.time_observer.timestamp()

    def _get_half_cycle_time_seconds(self):
        return (
            self.half_cycle_time_seconds_override
            if self.half_cycle_time_seconds_override is not None
            else self.half_cycle_time_seconds
        )

    def run(self):
        if not self.pump_should_be_on or self._get_half_cycle_time_seconds() <= 0:
            return

        # If the pump should be engaged, and the pump has been on for more than half a cycle, turn it off
        if (
            self.pump.is_pump_on()
            and (self.time_observer.timestamp() - self._last_half_cycle_timestamp)
            > self._get_half_cycle_time_seconds()
        ):
            self._internal_turn_off()
        # If the pump should be engaged, and the pump has been off for more than half a cycle, turn it on
        elif (
            self.pump.is_pump_off()
            and (self.time_observer.timestamp() - self._last_half_cycle_timestamp)
            > self._get_half_cycle_time_seconds()
        ):
            self._internal_turn_on()
