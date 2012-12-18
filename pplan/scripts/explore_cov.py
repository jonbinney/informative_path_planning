import sys, shelve, os.path, random
import numpy as np
from matplotlib import pyplot as plt
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

# read in the historical data
#s = shelve.open(os.path.join(run_dir, 'romsarchive.dat'))
#historical_data_dict = s['historical_data_dict']
#s.close()

# read in the list of points
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
points = s['points']
kmat = s['Kmat']
good_u_data = s['good_u_data']
good_v_data = s['good_v_data']
G = s['G']

times = sorted(set(points[:,-1]))[:-1]
times_exp = [(t_i+13-7-27) for t_i in times]

cmat = ppas.gaussian.correlation(kmat)

if 1:
    plt.figure()
    plt.title('Correlation vs. Time')
    plt.xlabel('Time (hours after experiment start)')
    plt.ylabel('Correlation')
    for sp in G.node_positions:
        Y = []
        for p_i in range(len(points)):
            p = points[p_i]
            if (p[:len(sp)] == sp).all() and p[-1] in times:
                Y.append(cmat[0,p_i])
        plt.plot(times_exp, Y)

if 1:
    plt.figure()
    plt.title('Easterly Current vs. Time')
    plt.xlabel('Time (hours after experiment start)')
    plt.ylabel('Correlation')
    for sp in G.node_positions:
        Y = []
        for p_i in range(len(points)):
            p = points[p_i]
            if (p[:len(sp)] == sp).all() and p[-1] in times:
                Y.append(cmat[0,p_i])
        plt.plot(times_exp, Y)        

# plot correlation against one of the dimensions
if 0:
    X = []
    Y = []
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Correlation vs. Time')
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Correlation')
    pref_i = 0
    for p_i in range(len(points)):
        p = points[p_i]
        if (p[:2] == points[100,:2]).all():
            c = Cmat[pref_i,p_i]
            X.append(p[3])
            Y.append(c)
    ax.plot(X, Y)

# plot value for one position against time
if 0:
    good_historical_data = s['good_historical_data']
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('%s vs. Time' % roi_properties['qoi'])
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel(roi_properties['qoi'])
    pref_i = 0
    for sample_i in [good_historical_data.shape[1] - 1]:
        X = []
        Y = []
        for p_i in range(len(points)):
            p = points[p_i]
            if (p[:2] == points[100,:2]).all():
                val = good_historical_data[p_i,sample_i]
                X.append(p[3])
                Y.append(val)
    print 'plotting...'
    ax.plot(X, Y)
    

# plot the values for one timestep, using one of the training samples
if 0:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Lat, Lon, %s' % roi_properties['qoi'])
    ax.set_xlabel('Lat')
    ax.set_ylabel('Lon')
    X = []
    Y = []
    C = []
    for p_i in range(len(points)):
        lat, lon, depth, t = points[p_i]
        if t == 6:
            val = good_historical_data[p_i,0]
            X.append(lon)
            Y.append(lat)
            C.append(val)
    if X:
        ax.scatter(X, Y, c=C)

s.close()
plt.show()
