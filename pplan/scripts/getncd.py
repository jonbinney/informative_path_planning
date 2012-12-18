import sys, shelve, os.path

import roslib
roslib.load_manifest('pplan')
from matplotlib import pyplot as plt
import ppas.roms

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# connect to ROMS
dset = ppas.roms.open_dataset(roi_properties['date'])

# get the data
lat0 = roi_properties['lat0'] - .1
lat1 = roi_properties['lat1'] + .1
lon0 = roi_properties['lon0'] - .1
lon1 = roi_properties['lon1'] + .1
depth0_i = roi_properties['depth0_i']
depth1_i = roi_properties['depth1_i']
time0_i = roi_properties['time0_i']
time1_i = roi_properties['time1_i']
data = ppas.roms.get_data(dset, lat0, lon0, lat1, lon1, time0_i, time1_i,
                     depth0_i, depth1_i)

# save the data
s = shelve.open(os.path.join(run_dir, 'romsdata.dat'))
s['data'] = data
s.close()
