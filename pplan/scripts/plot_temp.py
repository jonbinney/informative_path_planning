#!/usr/bin/env python
import roslib
roslib.load_manifest('pplan')
import sys, time, os, os.path, multiprocessing, datetime, signal
import numpy as np
from scipy import linalg
from matplotlib import pyplot as plt

import pplan, ppas

settings = pplan.PPlanSettings(sys.argv[1])
store = ppas.Store(settings.data_dir)
G = store['G']
points = store['points']
good_training_data = store['good_training_data']

for sp0 in G.node_points:
    point_indices = []
    for p_i in range(len(points)):
        d = linalg.norm(points[p_i][:2] - sp0)
        #print p_i, d
        if d < 0.001:
            point_indices.append(p_i)
    qoi_means = good_training_data.mean(axis=1)
    qoi_var = good_training_data.var(axis=1)

    times = (points[point_indices,3] - points[0,3])/3600.
    plt.plot(times, qoi_means[point_indices], '-')
    #plt.plot(times, qoi_var[point_indices], '-')
plt.show()
    
