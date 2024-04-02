from logging import Logger


class ValveLock:
    def __init__(self, logger: Logger):
        self.locked_in_id = -1
        self.logger = logger

    def acquire_lock(self, valve_id):
        valve_id = int(valve_id)

        if self.locked_in_id < 0:
            self.locked_in_id = valve_id
            return True

        return False

    def release_lock(self, valve_id):
        valve_id = int(valve_id)

        if self.locked_in_id == valve_id:
            self.locked_in_id = -1
            return True
        else:
            self.logger.warning(
                "Valve %d not owning the lock asked for a release of the lock"
            )
            return False

    def is_locked(self):
        return self.locked_in_id > 0
