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
