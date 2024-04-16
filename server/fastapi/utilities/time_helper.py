# Time helper

from datetime import datetime
from dateutil import tz
import time
import math


class TimeHelper:

    @staticmethod
    def format_timestamp_as_local(timestamp):
        if not timestamp:
            return 'Not a Timestamp: %s' % str(timestamp)

        dt_local = datetime.fromtimestamp(timestamp, tz.tzlocal())
        return dt_local.strftime("%Y/%m/%d %H:%M:%S")

    @staticmethod
    def format_timestamp_as_hour_time(timestamp):
        dt_local = datetime.fromtimestamp(timestamp, tz.tzlocal())
        return dt_local.strftime("%d %H:%M")

    @staticmethod
    def timestamp():
        # return round(time.time())
        # just for testing:
        return 1649324885

    @staticmethod
    def format_delta(seconds):
        days = math.floor(seconds / 86400)

        seconds = seconds - (days * 86400)

        hours = math.floor(seconds / 3600)

        seconds = seconds - (hours * 3600)

        minutes = math.floor(seconds / 60)

        seconds = seconds - (minutes * 60)

        delta_pieces = []

        if days > 0:
            delta_pieces.append('%d days' % days)

        if hours > 0:
            delta_pieces.append("%d hours" % hours)

        if minutes > 0:
            delta_pieces.append("%d minutes" % minutes)

        if seconds > 0:
            delta_pieces.append("%d seconds" % seconds)

        return ' '.join(delta_pieces)
