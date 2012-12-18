'''
Defines a standard way of representing time for ppas.

All ppas times which need a continuous representation of time should use
the number of seconds since 1970.1.1 00:00:00, as calculated by
the functions in this file. This is the same as POSIX (UNIX) time.

Note: Leap seconds are ignored.

2011.8.4 Jon Binney 
'''
import datetime, pytz

# zero time. doesn't matter when it is, as long as it never changes!
dt0 = pytz.utc.localize(datetime.datetime(1970, 1, 1, 0, 0))

def datetime_to_seconds(dt):
    tzname = dt.tzname()
    if tzname == None:
        # naive datetime, assume UTC
        dt = pytz.utc.localize(dt)
    elif tzname == 'UTC':
        # already in UTC
        pass
    else:
        # some other timezone. convert to UTC
        dt = dt.astimezone(pytz.utc)
    t_delta = dt - dt0
    return timedelta_to_seconds(t_delta)

def seconds_to_datetime(sec):
    return dt0 + seconds_to_timedelta(float(sec))

def timedelta_to_seconds(t_delta):
    return 24.*3600.*t_delta.days + t_delta.seconds + 1e-6*t_delta.microseconds

def seconds_to_timedelta(sec):
    return datetime.timedelta(seconds=float(sec))
