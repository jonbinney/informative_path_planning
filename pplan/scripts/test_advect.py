import sys, shelve, os.path, time
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

# load the ROMS data
s = shelve.open(os.path.join(run_dir, 'romsarchive.dat'))
historical_data_dict = s['historical_data_dict']
s.close()

# read in the list of points
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
points = s['points']
G = s['G']
s.close()

data = historical_data_dict[training_properties['dates'][-1]]
depth = roi_properties['depth']

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
plt.show()
timestep = 0.2
spatial_points = G.node_positions.copy()
lat_min = G.node_positions[:,0].min() - .1
lat_max = G.node_positions[:,0].max() + .1
lon_min = G.node_positions[:,1].min() - .1
lon_max = G.node_positions[:,1].max() + .1
for t in np.arange(0, 48, timestep):
    print t
    for sp_i in range(len(spatial_points)):
        sp = spatial_points[sp_i]
        lat_new, lon_new = ppas.roms.advect_point(
            data, sp[0], sp[1], depth, t, t+timestep, timestep)
        sp_new = np.array((lat_new, lon_new))
        spatial_points[sp_i,:] = sp_new
    ax.clear()
    ax.scatter(spatial_points[:,1], spatial_points[:,0])
    ax.set_xbound(lon_min, lon_max)
    ax.set_ybound(lat_min, lat_max)
    plt.draw()
    time.sleep(0.02)
