import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import gp, jgraph

def correlation(K):
    # construct the correlation matrix from the covariance matrix
    K = np.array(K)
    C = np.zeros((len(K), len(K)))
    for ii in range(len(K)):
        for jj in range(len(K)):
            C[ii][jj] = K[ii][jj] / (K[ii][ii]**0.5 * K[jj][jj]**0.5)
    return C

verbose = True

starttime = time.time()
def printdbg(msg_str, always=False):
    if verbose or always:
        print '%0.4f:' % (time.time()-starttime,), msg_str

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# load the graph, points, and precomputed kernel values from file
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
G = s['G']
print 'Graph has %d nodes' % len(G)
edgelen = s['edgelen']
points = s['points']
print 'Loaded %d points' % len(points)
Xi_pilot = s['Xi_pilot']
if empirical_cov:
    # use empirical covariance matrix
    print 'Using empirical covariance matrices'
    trials = s['trials']
    # redefine sigma_n to be the sampling noise
    sigma_n = 0.001
    Kmat = trials[0]['Kmat']
else:
    print 'Using GP kernel as covariance matrix'
    # use GP kernel as covariance matrix
    Kmat = s['Kmat']
sigma_n = s['sigma_n']
hdict = s['hdict']
s.close()

Xi_all = set(range(len(points)))  # all possible samples
xc = 34
Cmat = correlation(Kmat)

dlist = []
klist = []
clist = []
latdifflist = []
longdifflist = []
for xi in Xi_all:
    p1 = points[xi]
    p2 = points[xc]
    d = linalg.norm(p2 - p1)
    k = Kmat[xi,xc]
    dlist.append(d)
    latdifflist.append(p1[0]-p2[0])
    longdifflist.append(p1[1]-p2[1])
    klist.append(k)
    clist.append(Cmat[xc, xi])

plt.scatter(latdifflist, longdifflist, c=clist)
plt.scatter([0], [0], marker='x', s=100)
plt.title('Covariance plot')
plt.show()
