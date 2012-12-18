import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import roslib
roslib.load_manifest('pplan')
import ppas

pref_i = 0
pref = points[pref_i]

# plot k vs depth and distance for t=0
depth_list = []
distance_list = []
k_list = []
for p_i in range(len(points)):
    p = points[p_i]
    if p[-1] == 0:
        distance = linalg.norm(p[0:2]-points[0,0:2])
        depth = p[2]
        distance_list.append(distance)
        depth_list.append(depth)
        k_list.append(Kmat[pref_i, p_i])

