import sys, os, os.path, shelve
import numpy as np
from matplotlib import pyplot as plt

def path_to_positions(G, P):
    positions = []
    for p in P:
        positions.append(G.node_positions[p[0]])
    positions.append(G.node_positions[p[1]])
    return np.array(positions)

def plot_path(path):
    print 'plotting', path
    plt.plot([p[1] for p in path], [p[0] for p in path])
    
# set the directory for the run (where data files will be written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
G = s['G']
lm_spatial_points = s['lm_spatial_points']
P_grg = s['P_grg']
s.close()

grg_spatial_points = path_to_positions(G, P_grg)


plot_path(lm_spatial_points)
plot_path(grg_spatial_points)
plt.show()
