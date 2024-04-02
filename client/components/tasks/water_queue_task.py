from client.components.pump import Pump
from client.components.time_observer import TimeObserver
from client.components.valve_lock import ValveLock
from client.components.web_client import WebClient


class WaterQueueTask:
    def __init__(
        self,
        web_client: WebClient,
        run_every_seconds: int,
        valve_lock: ValveLock,
        valve_dict: dict,
        pump: Pump,
        time_observer: TimeObserver = None,
    ):
        self.web_client = web_client
        self.run_every_seconds = int(run_every_seconds)
        self.last_run_ts = 0
        self.valve_lock = valve_lock
        self.valve_dict = valve_dict
        self.pump = pump
        self.time_observer = time_observer or TimeObserver()

    def should_run(self):
        return self.time_observer.timestamp() > (
            self.last_run_ts + self.run_every_seconds
        )

    def run(self):
        if not self.should_run():
            return

        # If the valve is locked, just return without setting the time so it checks again soon
        if self.valve_lock.is_locked():
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
        if self.valve_lock.acquire_lock(next_valve_id):
            #            url = SERVER_URL + '/valves/watering-queue/%s' % next_valve_id
            #            response = requests.delete(url)
            #
            #            if response.status_code != 200:
            #                logging.error('Error received trying to dequeue valve')
            #                logging.error(response.json())
            #                return

            if not self.web_client.dequeue_valve(next_valve_id):
                return

            self.valve_dict[str(next_valve_id)].open(open_duration_seconds)
            self.pump.turn_on()
