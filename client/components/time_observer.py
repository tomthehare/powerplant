import time
import datetime


class TimeObserver:
    FIVE_MINUTES = 300
    TEN_MINUTES = 600
    FIFTEEN_MINUTES = 900

    def timestamp(self):
        return round(time.time())

    def current_day(self):
        return datetime.date.today().timetuple().tm_yday

    def current_hour(self):
        return datetime.datetime.now().hour

    def current_minute(self):
        return datetime.datetime.now().minute
