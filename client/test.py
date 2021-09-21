import time
import datetime
import pytz

pacific_now = datetime.datetime.now(pytz.timezone('America/New_York'))
print(pacific_now.utcoffset().total_seconds())
