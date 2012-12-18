import shelve, os.path
import roslib
roslib.load_manifest('pplan')
from matplotlib import pyplot as plt
import numpy as np

import ppas

run_dir = '/home/binney/Research/papers/2011_iros/runs/depth_transect/'

##############################################################################
# Settings
##############################################################################

# set the directory for the run (where data files will written to/read from)
print 'run_dir is', run_dir

# read variables in from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
graph_spatial_points = s['graph_spatial_points']
G = s['G']
points = s['points']
Xi_pilot = s['Xi_pilot']

