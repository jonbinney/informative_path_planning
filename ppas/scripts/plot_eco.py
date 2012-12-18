#!/usr/bin/env python
import roslib; roslib.load_manifest('ppas')
import csv, datetime, pytz, sys
import numpy as np
from matplotlib import pyplot as plt
import ppas

def filter_by_depth(data, min_depth, max_depth, debounce_seconds):
    ind = np.zeros((len(data),), dtype=np.bool)
    last_bad_t = data[0,0]
    for data_i in range(len(data)):
        t = data[data_i,0]
        depth = data[data_i,3]
        if depth < min_depth or depth > max_depth:
            last_bad_t = t
        if t - last_bad_t > debounce_seconds:
            ind[data_i] = True
    print ind.sum()
    return data[ind]

filename = sys.argv[1]

data = ppas.ecomapper.get_data_as_array(filename, [
    'Temp C', 'SpCond mS/cm', 'DTB Height (m)'])
#data = data[:800]
#data = data[data[:,3] < 0.01]

# throw out salinity outliers
print data.shape
#data[data[:,5]<.41,5] = .41

#filtered_data = filter_by_depth(data, 1.7, 2.1, 5.0)
filtered_data = data
print data.shape

ax1 = plt.subplot(3,1,1)
plt.title('Temp')
plt.plot(data[:,0], data[:,4], 'b-')
plt.plot(filtered_data[:,0], filtered_data[:,4], 'go')

ax2 = plt.subplot(3,1,2, sharex=ax1)
plt.title('Vehicle Depth')
plt.plot(data[:,0], -data[:,3], 'b-')
plt.plot(data[:,0], -(data[:,3]+data[:,6]), 'r-')

map_ax = plt.subplot(3,1,3)
temps = filtered_data[:,4]
c = (temps - temps.min()) / (temps.
                             max() - temps.min())
plt.plot(data[:,2], data[:,1], 'b-')
#plt.scatter(filtered_data[:,2], filtered_data[:,1], c=c, linewidths=0)

if len(sys.argv) > 2:
    filename_out = sys.argv[2]
    s = ppas.Store('.')
    s[filename_out] = filtered_data

plt.show()
