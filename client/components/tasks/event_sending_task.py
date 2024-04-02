from logging import Logger
import json
from client.components.event_client import EventClient
from client.components.web_client import WebClient


class EventSendingTask:
    def __init__(
        self,
        events_to_send,
        web_client: WebClient,
        event_client: EventClient,
        logger: Logger,
    ):
        self.events_to_send = events_to_send
        self.web_client = web_client
        self.event_client = event_client
        self.logger = logger

    def run(self):
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
