from logging import Logger
import json
from components.event_client import EventClient
from components.time_observer import TimeObserver
from components.web_client import WebClient


class EventSendingTask:
    def __init__(
        self,
        events_to_send,
        web_client: WebClient,
        event_client: EventClient,
        logger: Logger,
        run_every_seconds: int,
        time_observer: TimeObserver = None,
    ):
        self.events_to_send = events_to_send
        self.web_client: WebClient = web_client
        self.event_client: EventClient = event_client
        self.logger: Logger = logger
        self.last_ran_timestamp: int = 0
        self.failure_count: int = 0
        self.run_every_seconds: int = run_every_seconds
        self.time_observer = time_observer or TimeObserver()
        self.run_next_time: int = self.time_observer.timestamp() - 1

    def run(self):
        if self.time_observer.timestamp() <= self.run_next_time:
            return

        counter = 0
        while counter < self.events_to_send:
            counter = counter + 1
            details = self.event_client.get_earliest_event()

            if not details:
                break

            filename = details["filename"]
            payload = details["payload"]

            if self.web_client.post_event(payload):
                self.event_client.delete_event(filename)
                self.logger.info("Sent Event: %s" % json.dumps(payload))
                self.failure_count = 0
                self.run_next_time = (
                    self.time_observer.timestamp() + self.run_every_seconds
                )
            else:
                self.failure_count = self.failure_count + 1
                self.run_next_time = (
                    self._calculate_sleep_time() + self.time_observer.timestamp()
                )
                self.logger.info(
                    "Events failed to send - Will try again in %d seconds..."
                    % (self.run_next_time - self.time_observer.timestamp())
                )
                break

    def _calculate_sleep_time(self):
        sleep_max = 60
        current_expo_sleep = 2**self.failure_count

        return min(sleep_max, current_expo_sleep)
