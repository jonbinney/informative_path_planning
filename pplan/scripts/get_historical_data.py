import sys, shelve, os.path
import ppas

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))


# add a buffer around the region, so that we can interpolate points
# that are on the edge
lat0 = roi_properties['lat0'] - .03
lat1 = roi_properties['lat1'] + .03
lon0 = roi_properties['lon0'] - .03
lon1 = roi_properties['lon1'] + .03
time0_i = 0
time1_i = 71
depth0_i = 0
depth1_i = 11

historical_data_dict = {}
for date in training_properties['dates']:
    print 'Getting data for', date
    
    # connect to ROMS
    try:
        dset = ppas.roms.open_dataset(date)

        # get the data
        data = ppas.roms.get_data(
            dset, lat0, lon0, lat1, lon1, time0_i, time1_i,
                                  depth0_i, depth1_i)
        historical_data_dict[date] = data
    except Exception:
        print 'No ROMS data available for', date
    
    
# save the data
s = shelve.open(os.path.join(run_dir, 'romsarchive.dat'))
s['historical_data_dict'] = historical_data_dict
s.close()

