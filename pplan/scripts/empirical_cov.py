import sys, shelve, os.path, random
import numpy as np
from scipy import stats
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

varname = roi_properties['qoi']

if varname == 'salt':
    varmin, varmax = 30., 40.
    extra_noise = 0.0
elif varname == 'temp':
    varmin, varmax = 10., 100.
    extra_noise = 0.1

# read in the historical data
s = shelve.open(os.path.join(run_dir, 'romsarchive.dat'))
historical_data_dict = s['historical_data_dict']
s.close()

# read in the list of points
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
point_set = s['point_set']
s.close()

points = np.array(point_set.get_all_points())

# get rid of bad values
good_data_dict = {}
for date in historical_data_dict.keys():
    data = historical_data_dict[date]    
    has_bad_values = False
    for p in points:
        val = ppas.roms.get_value(data, p[0], p[1], p[2], p[3], varname,
                                  interp='linear')
        if val < varmin or val > varmax:
            has_bad_values = True
    if not has_bad_values:
        good_data_dict[date] = data
    else:
        print 'Bad values, throwing away data for', date

# create an array of values for each point
historical_data = []
good_u_data = []
good_v_data = []
for p in points:
    p_data_list = []
    p_u_list = []
    p_v_list = []
    for date in training_properties['dates']:
        if date in good_data_dict.keys():
            data = good_data_dict[date]
            val = ppas.roms.get_value(
                data, p[0], p[1], p[2], p[3], varname, interp='linear')
            u = ppas.roms.get_value(
                data, p[0], p[1], p[2], p[3], 'u', interp='linear')
            v = ppas.roms.get_value(
                data, p[0], p[1], p[2], p[3], 'v', interp='linear')
            noise = stats.distributions.norm.rvs(0.0, extra_noise)
            p_data_list.append(val+noise)
            p_u_list.append(u)
            p_v_list.append(v)
    historical_data.append(p_data_list)
    good_u_data.append(p_u_list)
    good_v_data.append(p_v_list)
good_historical_data = np.array(historical_data)
good_u_data = np.array(good_u_data)
good_v_data = np.array(good_v_data)

# calculate covariance and correlation
emp_cov = np.cov(np.array(historical_data))
emp_corr = np.corrcoef(np.array(historical_data))

# save the covariance matrix
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
s['kmat'] = emp_cov
s['good_historical_data'] = good_historical_data
s['good_u_data'] = good_u_data
s['good_v_data'] = good_v_data
s.close()

