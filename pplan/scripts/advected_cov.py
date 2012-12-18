import sys, shelve, os.path, time
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

# read in the list of points
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
points = s['points']
G = s['G']
s.close()

depth = roi_properties['depth']

plt.ion()

sigma_n = 0.01
sigma_f = 1.0
l_lat = 50.0
l_lon = 50.0
l_t = 0.1
hyper_params = np.array([sigma_n, sigma_f, l_lat, l_lon, l_t])

# timestep in hours for doing advection
timestep = .2

# create the kernel (will cache the advected positions for all of the points)
points_to_use = points
kernel = ppas.gp.kernels.AdvectedWeightedExponential(
    data, points_to_use, timestep)

kmat_awe = kernel.value(hyper_params[1:], points_to_use, points_to_use)

# read in the list of points
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
s['gp_awe'] = dict(
    kernel = kernel,
    kmat = kmat_awe
    )
s.close()
