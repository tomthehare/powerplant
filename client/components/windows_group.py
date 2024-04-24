from logging import Logger

from components.window import Window


class WindowsGroup:
    def __init__(self, windows_list: list, logger: Logger):
        self.windows = windows_list
        self.windows_are_open = None

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

    def close(self):
        if not self.eligible_for_close():
            self.logger.info("Windows are already closed")
            return

        for window in self.windows:
            window.close()

        self.windows_are_open = False
