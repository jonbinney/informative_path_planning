import re, datetime
import numpy as np
from scipy import linalg
from pydap.client import open_url

from util import *

def meters_to_degrees(u, v):
    '''
    Converts meters to degrees

    Estimated from google earth, for the area north of catalina
    '''
    return u/110500.0, v/92941.176

def degrees_to_meters(lat_deg, lon_deg):
    return 110500.0*lat_deg, 92941.176*lon_deg

def time_to_roms(data, time, side='left'):
    time_i = np.searchsorted(data['time'], time, side=side)
    return time_i

def depth_to_roms(data, depth, side='left'):
    depth_i = np.searchsorted(data['depth'], depth, side=side)
    return depth_i

def decdeg_to_roms(data, lat, lon, side='left'):
    lat_i = np.searchsorted(data['lat'], lat, side=side)
    lon_i = np.searchsorted(data['lon'], lon, side=side)
    return lat_i, lon_i

def roms_to_decdeg(data, lat_i, lon_i):
    return data['lat'][lat_i], data['lon'][lon_i]

def advect_point(data, lat0, lon0, depth, t0, t1, timestep):
    lat, lon = lat0, lon0
    for t in np.arange(t0, t1, timestep):
        u = get_value(data, lat, lon, depth, t, 'u')
        v = get_value(data, lat, lon, depth, t, 'v')
        lat_delta, lon_delta = meters_to_degrees(
            u*timestep*3600., v*timestep*3600.)
        lat += lat_delta
        lon += lon_delta
    return lat, lon

def get_value(data, lat, lon, depth, time, qoi, interp='linear'):
    '''
    Return the ROMS value for the given position and time. Uses trilinear
    interpolation by default.

    Note: Doesnt interpolate along the time axis right now - just chooses
    the nearest time. Should fix this and use a proper interpolation routine.

    Algorithm taken from:
    http://en.wikipedia.org/wiki/Trilinear_interpolation
    '''
    # find the corners of the cube around this point
    lat_i = np.searchsorted(data['lat'], lat) - 1
    depth_i = np.searchsorted(data['depth'], depth) - 1
    lon_i = np.searchsorted(data['lon'], lon) - 1
    lat0, lat1 = data['lat'][lat_i], data['lat'][lat_i+1]
    lon0, lon1 = data['lon'][lon_i], data['lon'][lon_i+1]
    depth0, depth1 = data['depth'][depth_i], data['depth'][depth_i+1]
    time_i = np.searchsorted(data['time'], time)

    if time < data['time'][0]:
        die_bad_time_

    if interp == 'linear':
        # calculate interpolation coefficients
        lat_d = (lat - lat0) / (lat1 - lat0)
        lon_d = (lon - lon0) / (lon1 - lon0)
        depth_d = (depth - depth0) / (depth1 - depth0)
        
        # interpolate along depth axis
        v = data[qoi][time_i,...]
        i1 = (v[depth_i,lat_i,lon_i]*(1 - depth_d)
              + v[depth_i+1,lat_i,lon_i]*depth_d)
        i2 = (v[depth_i,lat_i,lon_i+1]*(1 - depth_d) +
              v[depth_i+1,lat_i,lon_i+1]*depth_d)
        j1 = (v[depth_i,lat_i+1,lon_i]*(1-depth_d)
              + v[depth_i+1,lat_i+1,lon_i]*depth_d)
        j2 = (v[depth_i,lat_i+1,lon_i+1]*(1 - depth_d)
              + v[depth_i+1,lat_i+1,lon_i+1]*depth_d)

        # interpolate along longitude axis
        w1 = i1*(1 - lon_d) + i2*lon_d
        w2 = j1*(1 - lon_d) + j2*lon_d

        # interpolate along latitude axis
        val = w1*(1 - lat_d) + w2*lat_d
    elif interp == 'round':
        # round down to the next lower point
        v = data[qoi][time_i,...]
        val = v[depth_i,lat_i,lon_i]
    return val
    
def open_dataset(date):
    dataset = open_url(
        'http://ourocean.jpl.nasa.gov:8080/thredds/dodsC/las/scb_fcst_%d%02d%02d03.nc' % (
            date.year, date.month, date.day))
    return dataset

def get_data(dataset, lat0, lat1, lon0, lon1, depth0, depth1, time0=None, time1=None):
    '''
    Get data between lat0, lon0 and lat1, lon1, and time0, time1, and depth0, depth1.
    Lat and lon are in decimal degrees; times are python.datetime objects, and depth in meters.

    Returns data as a dictionary with time, depth, lat, lon, u, v, temp, and salt arrays.
    '''
    time_unit_str = dataset['time'].attributes['units']
    m = re.match('hour since (\d+)-(\d+)-(\d+) 13:00:00', time_unit_str)
    if m:
        year, month, day = [int(s) for s in m.groups()]
        dataset_offset_seconds = datetime_to_seconds(datetime.datetime(year, month, day, 13))
    else:
        dieee_bad_time_unit_str_____

    # convert time from <hours after ___> to seconds since 1970,1,1 00:00:00
    time_arr = 3600.*dataset['time'][:] + dataset_offset_seconds
    if time0:
        time0_i = np.max([np.searchsorted(time_arr, time0) - 1, 0])
    else:
        time0_i = 0
    if time1:
        time1_i = np.searchsorted(time_arr, time1) + 1
    else:
        time1_i = len(time_arr) - 1
    
    # get the latitude and longitude arrays first, so that we can figure
    # out what indices we need to grab for our data
    lat_arr = dataset['lat'][:]
    lon_arr = dataset['lon'][:] % 360 - 360
    depth_arr = dataset['depth'][:]

    latlon_dict = {'lat':lat_arr, 'lon':lon_arr}
    lat0_i, lon0_i = decdeg_to_roms(latlon_dict, lat0, lon0, side='right')
    lat1_i, lon1_i = decdeg_to_roms(latlon_dict, lat1, lon1)
    depth0_i = np.max([np.searchsorted(depth_arr, depth0) - 1, 0])
    depth1_i = np.searchsorted(depth_arr, depth1)

    # indices to retrieve data for
    ind = np.index_exp[
        time0_i:time1_i,depth0_i:depth1_i,lat0_i:lat1_i,lon0_i:lon1_i]
    shape = (time1_i - time0_i, depth1_i - depth0_i,
             lat1_i - lat0_i, lon1_i - lon0_i)

    # now grab the data we want
    data = {}
    data['u'] = np.reshape(dataset['u']['u'][ind], shape)
    data['v'] = np.reshape(dataset['v']['v'][ind], shape)
    data['w'] = np.reshape(dataset['w']['w'][ind], shape)    
    data['temp'] = np.reshape(dataset['temp']['temp'][ind], shape)
    data['salt'] = np.reshape(dataset['salt']['salt'][ind], shape)
    data['lat'] = lat_arr[lat0_i:lat1_i]
    data['lon'] = lon_arr[lon0_i:lon1_i]
    data['depth'] = depth_arr[depth0_i:depth1_i]
    data['time'] = time_arr[time0_i:time1_i]
    return data
    
def glider_travel_time(data, start_t, start_p, end_p, dive_params):
    '''
    Calculate how long it will take the robot to travel from start_p to
    end_p, starting at time start_t, if it moves at velocity robot_velocity.
    Takes into account the predicted currents.
    '''
    num_increments = 10. # fairly arbitrary
    increments = np.linspace(0.0, 1.0, num_increments)
    effective_speeds = []
    num_dives = 20 # FIXME - should calculate from dive_params['dive_spacing']
    positions = []
    for inc in increments:
        # we simplify the problem by pretending that the glider travels
        # in a straight line between the start and end points, and that only
        # its speed is affected by the currents.  this would be the case
        # if the current was never faster than the glider, and the glider
        # changed direction underwater to cancel out the effects of the
        # current.  in reality, the glider is not this smart (right?)
        lat, lon = start_p + inc*(end_p - start_p)
        depth = 0.5*(dive_params['max_depth'] - dive_params['min_depth'])*(
            1.0 - np.cos(num_dives *2*np.pi * inc)) + dive_params['min_depth']
        depth_i = depth_to_roms(data, depth)
        lat_i, lon_i = decdeg_to_roms(data, lat, lon)
        time_i = time_to_roms(data, start_t)
        positions.append((time_i, depth_i, lat_i, lon_i))

    for time_i, depth_i, lat_i, lon_i in positions:
        u = data['u'][time_i, depth_i, lat_i, lon_i]
        v = data['v'][time_i, depth_i, lat_i, lon_i]
        current_vel = np.array(meters_to_degrees(u, v))

        # find the direction which the glider must aim for in order
        # to cancel the effect of the current.  going through a bunch
        # of possible angles is a bit of a hack; we really ought to
        # explicitly solve for the best angle.
        desired_dir = (end_p - start_p) / linalg.norm(end_p - start_p)
        # FIXME - glider speed should actually be kept in m/s for this
        # entire calculation, as should everything else.  when units are
        # in degrees, the speed depends (a little) on the direction  :-(
        g_speed = meters_to_degrees(dive_params['horizontal_vel'], 0)[0]
        g_dir_best = None
        theta_best = None
        err_best = np.inf
        for theta in np.linspace(0, 2*np.pi, 16):
            g_dir = np.array((np.cos(theta), np.sin(theta)))
            eff_vel = g_speed*g_dir + current_vel
            eff_dir = eff_vel / linalg.norm(eff_vel)
            err = np.arccos(np.dot(eff_dir, desired_dir))
            if err < err_best:
                g_dir_best = g_dir
                theta_best = theta
                err_best = err

        eff_vel = g_speed*g_dir_best + current_vel
        eff_speed = linalg.norm(eff_vel)
        if eff_speed <= 0.0:
            # current is moving too fast for the glider. hopeless! give up!
            current_too_fast_for_glider
        effective_speeds.append(eff_speed)

    travel_time = 0.0
    distance_increment = linalg.norm(end_p - start_p)/num_increments
    for speed in effective_speeds:
        travel_time += distance_increment / speed
        
    return travel_time

