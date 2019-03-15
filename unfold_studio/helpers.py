import pytz

utc = pytz.timezone('utc')

def localize(dt):
    "Ensures the datetime is tz-aware, in UTC"
    return dt if dt.tzinfo else utc.localize(dt)
