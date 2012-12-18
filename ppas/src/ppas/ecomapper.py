import csv, datetime, pytz
import numpy as np
from matplotlib import pyplot as plt
import ppas

def parse_time(date_str, time_str, timezone=pytz.utc):
    '''  Parse the ecomapper time format
    
    date_str is in format mm/dd/yyyy
    time_str is format hh:mm:ss.ss

    Returns ppas time as defined in ppas/util.py
    '''
    month_str, day_str, year_str = date_str.split('/')
    hour_str, min_str, float_sec_str = time_str.split(':')
    float_sec = float(float_sec_str)
    dt = datetime.datetime(int(year_str), int(month_str), int(day_str),
        int(hour_str), int(min_str), int(float_sec), int((float_sec%1)*1e6))
    ldt = timezone.localize(dt)
    return ppas.datetime_to_seconds(ldt)

def get_data_as_array(filename, fields):
    '''
    Returns an array in which each column has the values for a specific
    variable. Time, Lat., Lon., and Depth are always the frist four columns.
    User specified fields are the rest of the columns.

    reader - python csv.DictReader for the data file
    fields - list of field names to put into the array
    '''
    reader = csv.DictReader(open(filename), delimiter=';')
    data = []
    for field_dict in reader:
        time_str = field_dict['Time']
        date_str = field_dict['Date']
        time = parse_time(date_str, time_str)
        lat = float(field_dict['Latitude'])
        lon = float(field_dict['Longitude'])
        depth = float(field_dict['Depth meters'])
        vals = [time, lat, lon, depth]
        for f in fields:
            vals.append(float(field_dict[f]))
        data.append(vals)
    return np.array(data)
