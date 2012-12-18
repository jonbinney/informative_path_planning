import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import ppas

def make_path(G, start_t, node_list):
    t = start_t
    P = []
    for v_i, v_j in zip(node_list[:-1], node_list[1:]):
        P.append((v_i, v_j, t, 0))
        t += G.edge_length(v_i, v_j, t, 0)
    return P

# load the optimal path
# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# load the graph, points, and precomputed kernel values from file
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
G = s['G']
P_grg = s['P_grg']
points = s['points']
s.close()

fig = plt.figure()
ax = fig.add_subplot(111)
gplot = ppas.pplan.GraphPlotter(G)
#gplot.plot_path(P_grg)
gplot.plot(ax, t=25)
plt.scatter(points[:,1], points[:,0])

plt.show()

