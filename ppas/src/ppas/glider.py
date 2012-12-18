import re, os.path
import numpy as np

def webb_to_decdeg(webb):
    degrees = np.floor(np.abs(webb)/100.)
    minutes = np.abs(webb) % 100
    return np.sign(webb) * (degrees + minutes/60)

def decdeg_to_webb(decdeg):
    degrees = float(int(decdeg))
    minutes = (decdeg - degrees)*60.
    return degrees*100 + minutes

def make_ma(filename, waypoint_list, loop=False):
    '''
    Writes a goto file in the webb slocum glider format.

    waypoint_list - list of lat, lon pairs in decimal degree format
    filename - (optional) filename to write output to

    Notes:
    num_legs_to_run: -1 for loop or -2 to run the whole thing once
    initial_wpt: -2 for closest or 0 for first waypoint
    '''
    if loop:
        loop_str = '-1'
    else:
        loop_str = '-2'
    
    ma_str = ''
    ma_str += 'behavior_name=goto_list\n\n'
    ma_str += '#\n'
    ma_str += '<start:b_arg>\n'
    ma_str += 'b_arg: num_legs_to_run(nodim) %s\n' % loop_str
    ma_str += 'b_arg: start_when(enum) 0 # BAW_IMMEDIATELY\n'
    ma_str += 'b_arg: list_stop_when(enum) 7 # BAW_WHEN_WPT_DIST\n'
    ma_str += 'b_arg: initial_wpt(enum) 0 # closest\n'
    ma_str += 'b_arg: num_waypoints(nodim) %d\n' % len(waypoint_list)
    ma_str += '<end:b_arg>\n'
    ma_str += '<start:waypoints>\n'
    for lat, lon in waypoint_list:
        webb_lat = decdeg_to_webb(lat)
        webb_lon = decdeg_to_webb(lon)
        ma_str += '%.4f\t%.4f\n' % (webb_lon, webb_lat)
    ma_str += '<end:waypoints>\n'
    if filename:
        f = open(filename, 'w+')
        print >> f, ma_str
        f.close()
    return ma_str

def make_mi_from_template(template_filename, goto_num, output_path):
    output_filename, output_ext = os.path.splitext(os.path.split(output_path)[-1])
    if len(output_filename) > 8:
        print 'WARNING: MISSION FILENAME LONGER THAN 8 CHARACTERS!!'
    elif output_ext != '.mi':
        print 'WARNING: MISSION FILENAME DOES NOT END IN .mi!!'

    template_str = open(template_filename).read()
    mi_string = re.sub('_GOTO_NUM_', str(goto_num), template_str)
    f_out = open(output_path, 'w+')
    f_out.write(mi_string)
    f_out.close()
