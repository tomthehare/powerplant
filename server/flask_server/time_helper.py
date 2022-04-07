# Time helper

from datetime import datetime
from dateutil import tz

def format_timestamp_as_local(timestamp):
    dt_local = datetime.fromtimestamp(timestamp, tz.tzlocal())
    return dt_local.strftime("%Y/%m/%d %H:%M:%S")

def format_timestamp_as_hour_time(timestamp):
    dt_local = datetime.fromtimestamp(timestamp, tz.tzlocal())
    return dt_local.strftime("%d %H:%M")

def timestamp():
    return round(time.time())
