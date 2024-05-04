from logging import Logger
from components.pump import Pump
from components.tasks.water_queue_task import WaterQueueTask
from components.time_observer import TimeObserver
from components.valve_lock import ValveLock
from components.web_client import WebClient


class FakeWaterQueueTask(WaterQueueTask):
    def __init__(
        self,
        logger: Logger,
        web_client: WebClient,
        run_every_seconds: int,
        valve_lock: ValveLock,
        valve_dict: dict,
        pump: Pump,
        time_observer: TimeObserver = None,
    ):
        super().__init__(
            logger,
            web_client,
            run_every_seconds,
            valve_lock,
            valve_dict,
            pump,
            time_observer=time_observer,
        )

    def should_run(self):
        return self.time_observer.timestamp() > (
            self.last_run_ts + self.run_every_seconds
        )

    def run(self):
        if not self.should_run():
            return

        watering_queue = self.web_client.read_watering_queue()

        if not watering_queue:
            self.last_run_ts = self.time_observer.timestamp()
            return

        # If the queue is > 1 entry, we should immediately jump into the next one, not wait
        if len(watering_queue) == 1:
            self.last_run_ts = self.time_observer.timestamp()

        next_valve_id = watering_queue[0]["valve_id"]
        open_duration_seconds = watering_queue[0]["open_duration_seconds"]

        if not self.web_client.dequeue_valve():
            return

        self.logger.info(
            "[Fake] Opened valve %d for %d seconds"
            % (next_valve_id, open_duration_seconds)
        )
        self.logger.info("[Fake] Closed valve %d" % next_valve_id)
