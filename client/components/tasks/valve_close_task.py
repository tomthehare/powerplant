from logging import Logger

from client.components.pump import Pump
from client.components.time_observer import TimeObserver
from client.components.valve import Valve
from client.components.valve_lock import ValveLock


class ValveCloseTask:
    def __init__(
        self,
        valve: Valve,
        valve_lock: ValveLock,
        config,
        pump: Pump,
        logger: Logger,
        time_observer: TimeObserver = None,
    ):
        self.valve = valve
        self.valve_lock = valve_lock
        self.config = config
        self.pump = pump
        self.logger = logger
        self.time_observer = time_observer or TimeObserver()

    def run(self):
        # if int(self.valve.override_open_duration_seconds) < 0:
        #    closing_time = self.valve.last_opened_time + self.config.get_valve_config(self.valve.id).open_duration_seconds
        # else:
        #    closing_time = self.valve.last_opened_time + int(self.valve.override_open_duration_seconds)

        closing_time = (
            self.valve.last_opened_time
            + self.config.get_valve_config(self.valve.id).open_duration_seconds
        )

        if self.valve.is_open:
            self.logger.debug(
                "Right now its %d, will close valve at %d",
                self.time_observer.timestamp(),
                int(closing_time),
            )

        if self.valve.is_open and self.time_observer.timestamp() > int(closing_time):
            self.pump.turn_off()
            self.valve.close()
            self.valve_lock.release_lock(self.valve.id)
            return True

        return False
