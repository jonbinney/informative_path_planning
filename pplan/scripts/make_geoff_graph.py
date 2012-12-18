#!/usr/bin/env python
import sys, shelve, os.path

import roslib
roslib.load_manifest('pplan')

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

s = shelve.open(os.path.join(run_dir, 'data.shelf'))
node_positions = s['node_positions']
s.close()

s = shelve.open(os.path.join(run_dir, 'romsdata.dat'))
data = s['data']
s.close()

# restrict ourselves to a smaller area
graph_spatial_points = np.array([(lat, lon) for (lat, lon) in node_positions if lon > -119.0])

plt.scatter(graph_spatial_points[:,1], graph_spatial_points[:,0])
plt.title('Node positions')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

f = open(os.path.join(run_dir, 'graph.txt'), 'w+')

print >> f, '# graph with %d nodes' % len(graph_spatial_points)

edge_lengths = []
nodes = range(len(graph_spatial_points))
for v_i in nodes:
    sp_i = graph_spatial_points[v_i]
    for v_j in nodes:
        if v_i == v_j:
            continue
        sp_j = graph_spatial_points[v_j]
        if linalg.norm(sp_i - sp_j) < 1.0:
            edge_seconds = ppas.roms.glider_travel_time(
                data, 0, sp_i, sp_j, dive_params)
            x, y = ppas.roms.degrees_to_meters(sp_i[0]-sp_j[0], sp_i[1] - sp_j[1])
            edge_meters = (x**2 + y**2)**0.5
            print 'Creating edge from node %d to node %d of time %f hours, %f km' % (
                v_i, v_j, edge_seconds/3600., edge_meters/1000.)
            print >> f, '%d %d %f' % (v_i, v_j, edge_seconds/3600.)
            edge_lengths.append(edge_seconds/3600.)
            plt.plot([sp_i[1], sp_j[1]], [sp_i[0], sp_j[0]], 'b-')
f.close()

plt.figure()
plt.hist(edge_lengths)
plt.title('Histogram of edge lengths')
plt.xlabel('Length (hours)')
plt.ylabel('# occurances')

plt.show()
