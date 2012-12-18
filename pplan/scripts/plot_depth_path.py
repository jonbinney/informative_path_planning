import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import ppas

# optimal path found by the algorithm (length of 45)
P = [(0, 1, 0, 4),
     (1, 2, 6, 1),
     (2, 3, 11, 3),
     (3, 4, 16, 2),
     (4, 5, 20, 0),
     (5, 6, 26, 4),
     (6, 7, 33, 0),
     (7, 8, 38, 2)]

ppas.init()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xticks([])
ax.invert_yaxis()
sp_0 = graph_spatial_points[0]

# plot the depth profile
ii = 0
x_list = [0]
y_list = [0]
for (v_i, v_j, t, edge_num) in P:
    sp_i = graph_spatial_points[v_i]
    sp_j = graph_spatial_points[v_j]
    x_i = linalg.norm(sp_i - sp_0)
    x_j = linalg.norm(sp_j - sp_0)
    d_i = graph_properties['depth_list'][edge_num]
    x_list += [ii, ii+1]
    y_list += [d_i, d_i]
    ii += 1

x_list += [ii]
y_list += [0]

ax.set_title('Depth profile for B=23.5 hours')
ax.plot(x_list, y_list, 'b-')
ax.set_xbound(-1, 9)
ax.set_ybound(0, 110)
ax.set_ylabel('Depth in meters')
plt.show()
