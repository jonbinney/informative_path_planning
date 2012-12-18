import sys, shelve, os.path, datetime
from matplotlib import pyplot as plt
import ppas.roms

# connect to ROMS
dset = ppas.roms.open_dataset(datetime.date(2010, 7, 15))

# get the data
lat0 = 33.58
lon0 = -118.32
lat1 = 33.62
lon1 = -118.27
time0_i = 0
time1_i = 71
depth0_i = 0
depth1_i = 2
data = ppas.roms.get_data(dset, lat0, lon0, lat1, lon1, time0_i, time1_i,
                     depth0_i, depth1_i)

