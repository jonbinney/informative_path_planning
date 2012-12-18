import sys, shelve, os.path
import numpy as np
from matplotlib import pyplot as plt

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# load the stored roms data for this run
s = shelve.open(os.path.join(run_dir, 'romsarchive.dat'))
data_list = s['data_list']
s.close()

# plot the data
lat = data_list[0]['lat']
lon = data_list[0]['lon']
salt_min = np.min([data['salt'][0,0,:,:].min() for data in data_list])
salt_max = np.max([data['salt'][0,0,:,:].max() for data in data_list])
ndays = len(data_list)
fig = plt.figure()
for day in range(ndays):
    salt = data_list[day]['salt']
    ax = fig.add_subplot(np.ceil(ndays**.5),np.ceil(ndays**.5),day+1)
    ax.imshow(salt[0,0,...], interpolation='nearest',
              extent=[lon[0]-.01, lon[-1]+.01, lat[0]-.01, lat[-1]+.01],
              vmin=salt_min, vmax=salt_max)
    ax.set_xticks([])
    ax.set_yticks([])
plt.show()
