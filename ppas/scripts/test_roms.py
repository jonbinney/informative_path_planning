import roslib
roslib.load_manifest('ppas')
import datetime
import numpy as np
import ppas

lat0 = 33.4967
lon0 = -118.72
lat1 = 33.58
lon1 = -118.52
depth0 = 30.
depth1 = 50.

year, month, day = 2011, 7, 26

# get 3 hours of data starting at 15:00 GMT
time0 = ppas.datetime_to_seconds(datetime.datetime(year, month, day, 15))
time1 = time0 + 3.*3600.

print 'Connecting to ROMS server'
dataset = ppas.roms.open_dataset(datetime.date(year, month, day))

print 'Downloading data'
data = ppas.roms.get_data(dataset, lat0, lat1, lon0, lon1, depth0, depth1, time0, time1)

# print somve values
lat = (lat0 + lat1)/2.0
lon = (lon0 + lon1)/2.0
depth = (depth0 + depth1)/2.0
for t in np.linspace(time0, time1):
    v = ppas.roms.get_value(data, lat, lon, depth, t, 'temp', interp='linear')
    print 'Temperature at (%.3f, %.3f, %.1f, %.7f): %f' % (lat, lon, depth, t, v) 

