import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import roslib
roslib.load_manifest('pplan')
import ppas

fig = plt.figure()
ax = fig.add_subplot(111)
sp_0 = graph_spatial_points[0]
for e in P:
    sp_i = graph_spatial_points[e.v_i]
    d_i = linalg.norm(sp_i - sp_0)
    sp_j = graph_spatial_points[e.v_j]
    d_j = linalg.norm(sp_j - sp_0)
    ax.plot([d_i, d_j], [e.info['depth'], e.info['depth']])
    
ax.scatter(points[:,0], points[:,1])
ax.set_xticks([])
ax.set_yticks([])
ppas.graph.plot_path(ax, P, points, linestyle='-',)
plt.show()
