import sys, shelve, os.path
from matplotlib import pyplot as plt
import numpy as np
from scipy import linalg
import ppas

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

# load the ROMS data
s = shelve.open(os.path.join(run_dir, 'romsdata.dat'))
data = s['data']
s.close()

# each cell in the grid is 2x2km
start_t = 8
sp0 = np.array((data['lat'].min(), data['lon'].max()))
sp1 = np.array((data['lat'].max(), data['lon'].min()))

waypoints = [(1-r)*sp0 + r*sp1 for r in np.linspace(0, 1, 5)]

for sp_i, sp_j in zip(waypoints[:-1], waypoints[1:]):
    t1 = ppas.roms.glider_travel_time(data, start_t, sp_i, sp_j, dive_params)
    t2 = ppas.roms.glider_travel_time(data, start_t, sp_j, sp_i, dive_params)
    print '%4.2f, %4.2f' % (t1/3600., t2/3600.)

