from logging import Logger

from components.event_client import EventClient


class WindowsGroup:
    def __init__(self, windows_list: list, logger: Logger, event_client: EventClient):
        self.windows = windows_list
        self.windows_are_open = None
        self.event_client = event_client

    def eligible_for_open(self):
        if self.windows_are_open is None or self.windows_are_open == False:
            return True

        return False

    def eligible_for_close(self):
        if self.windows_are_open is None or self.windows_are_open == True:
            return True
        return False

    def open(self):
        if not self.eligible_for_open():
            self.logger.info("Windows are already open")
            return

        for window in self.windows:
            window.open()

        self.windows_are_open = True
        self.event_client.log_window_opened_event('all')

    def close(self):
        if not self.eligible_for_close():
            self.logger.info("Windows are already closed")
            return

        for window in self.windows:
            window.close()

        self.windows_are_open = False
        self.event_client.log_window_closed_event('all')
