import sys, shelve, os.path
from matplotlib import pyplot as plt
import numpy as np
from scipy import linalg
import ppas

##############################################################################
# Functions
##############################################################################

##############################################################################
# Settings
##############################################################################

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# read variables in from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

##############################################################################
# Main
##############################################################################

# make the grid
points_list = []
depth = roi_properties['depth']
lat0 = roi_properties['lat0']
lat1 = roi_properties['lat1']
lon0 = roi_properties['lon0']
lon1 = roi_properties['lon1']
start_t = planner_settings['start_t']
end_t = planner_settings['end_t']
times = range(0,49,1)
for lat in np.linspace(lat0, lat1, 3):
    for lon in np.linspace(lon0, lon1, 3):
        for t in times:
            p = np.array((lat, lon, depth, t))
            points_list.append(p)
points = np.array(points_list)

# save everything to a python shelf
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
s['points'] = points
s.close()
