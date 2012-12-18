import roslib; roslib.load_manifest('ppas')
import time, datetime
import ppas

# get the current POSIX time
t = time.time()

# convert to UTC datetime
tm = time.gmtime(t)
dt = datetime.datetime(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)

# convert back to POSIX time using our own function
t_ppas = ppas.datetime_to_seconds(dt)

# error should be less than one second (time.gmtime rounds to the nearest second)
print 'Error:', t - t_ppas
