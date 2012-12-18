import roslib; roslib.load_manifest('pplan')
import sys, shelve, os.path, random, time
import numpy as np
from scipy import linalg
from matplotlib import pyplot as plt
import ppas, pplan

##############################################################################
# Settings
##############################################################################

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

settings = pplan.PPlanSettings(run_dir)
s = ppas.Store(settings.data_dir)

##############################################################################
# Main
##############################################################################

# read in the historical data
#s = shelve.open(os.path.join(run_dir, 'romsarchive.dat'))
#historical_data_dict = s['historical_data_dict']
#s.close()

# read in the list of points
G = s['G']
points = s['points']
kmat = s['kmat']
#good_u_data = s['good_u_data']
#good_v_data = s['good_v_data']

times = sorted(set(points[:,-1]))
#mean_u_data = good_u_data.mean(axis=1)
#mean_v_data = good_v_data.mean(axis=1)

plt.ion()


lat_min = points[:,0].min()
lat_max = points[:,0].max()
lon_min = points[:,1].min()
lon_max = points[:,1].max()
border_width = 0.1*(lat_max - lat_min)
lat_min -= border_width
lat_max += border_width
lon_min -= border_width
lon_max += border_width

# pick the reference point
sp_ref = G.node_points[12]
t_ref = sorted(points[:,-1])[len(points)/2+1] 
p_ref_i = -1
dists = []
for p_i in range(len(points)):
    p = points[p_i]
    d = linalg.norm(sp_ref - p[:2])
    dists.append(d)
    if (d < 0.000001) and t_ref == points[p_i,-1]:
        print d
        p_ref_i = p_i
p_ref = points[p_ref_i]

times = times[:-1:2]
srows = 2
scols = np.ceil(len(times)/float(srows))
cmat = ppas.gaussian.correlation(kmat)
cmin = cmat[p_ref_i,:].min()
fig = plt.figure()
for t_i in range(len(times)):
    t = times[t_i]
    ax = fig.add_subplot(srows, scols, t_i+1)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_title('Hour %d' % (round(t-times[0])/3600,))

    X, Y, U, V = [], [], [], []
    for p_i in range(len(points)):
        p = points[p_i]
        if p[-1] == t:
            c = cmat[p_ref_i,p_i]
            col = plt.cm.jet( (c - cmin) / (1.0 - cmin) )
            sc_obj = ax.scatter([p[1]], [p[0]], c=col, s=64)

            #lat_u, lat_v = ppas.roms.meters_to_degrees(
            #    mean_u_data[p_i], mean_v_data[p_i])
            X.append(p[1])
            Y.append(p[0])
            #U.append(lat_u)
            #V.append(lat_v)

    if t == t_ref:
        ax.scatter([p_ref[1]], [p_ref[0]], marker='x', s=400, c='r')

    #Q = ax.quiver(X, Y, U, V)
    ax.set_xbound(lon_min, lon_max)
    ax.set_ybound(lat_min, lat_max)

cax = fig.add_axes([0.93, 0.1, 0.02, 0.8])
sm = plt.cm.ScalarMappable()
sm.set_array(np.linspace(cmin, 1.0, 10))
plt.colorbar(sm, cax=cax)

plt.show()

