import sys, shelve, os.path
import numpy as np
from matplotlib import pyplot as plt

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# load the stored roms data for this run
s = shelve.open(os.path.join(run_dir, 'romsdata.dat'))
romsdata = s['data']
s.close()

# plot the data
lat = romsdata['lat']
lon = romsdata['lon']
salt = romsdata['salt']
salt_min = salt[:,0,:,:].min()
salt_max = salt[:,0,:,:].max()
T = len(romsdata['time'])
fig = plt.figure()
for t in range(T):
    ax = fig.add_subplot(np.ceil(T**.5),np.ceil(T**.5),t+1)
    ax.imshow(romsdata['salt'][t,0,...], interpolation='nearest',
              extent=[lon[0]-.01, lon[-1]+.01, lat[0]-.01, lat[-1]+.01],
              vmin=salt_min, vmax=salt_max)
    ax.set_xticks(lon)
    ax.set_xticklabels(['%.2f' % l for l in lon])
    ax.set_yticklabels(['%.2f' % l for l in lat])
    ax.set_yticks(lat)
plt.show()
