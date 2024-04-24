from logging import Logger
from components.time_observer import TimeObserver


class TimeObserverTest(TimeObserver):

    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        super().__init__()

    def sleep(self, seconds: int):
        self.logger.info("I AM SLEEPING %d SECONDS zzzz...." % seconds)
