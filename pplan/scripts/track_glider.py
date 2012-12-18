import sys, re, urllib2, datetime
import numpy as np
from matplotlib import pyplot as plt

def plot_path(path, c='g'):
    plt.plot([p[1] for p in path], [p[0] for p in path], '-o', linewidth=4.0,
             alpha=0.7, c=c)

def path_to_positions(G, P):
    positions = []
    for p in P:
        positions.append(G.node_positions[p[0]])
    positions.append(G.node_positions[p[1]])
    return np.array(positions)

def webb_to_decdeg(webb):
    degrees = np.floor(np.abs(webb)/100.)
    minutes = np.abs(webb) % 100
    return np.sign(webb) * (degrees + minutes/60.)

def get_log_location(log_str):
    # GPS Location:  3401.218 N -11817.109 E measured
    m = re.search('GPS Location:\s+(\S+)\s+N\s+(\S+)', log_str)
    if m:
        lat_str, lon_str = m.groups()
        webb_lat, webb_lon = float(lat_str), float(lon_str)
        lat, lon = webb_to_decdeg(webb_lat), webb_to_decdeg(webb_lon)
        if lat < 1e3 and lon < 1e3:
            return lat, lon
    return None

def get_all_locations(logs):
    locations = []
    for t in sorted(logs):
        log_str = logs[t]
        loc = get_log_location(log_str)
        if loc:
            locations.append(loc)
    return np.array(locations)

def log_date(log_url):
    m = re.search(
        '([0-9]{4})([0-9]{2})([0-9]{2})T([0-9]{2})([0-9]{2})([0-9]{2})\.log',
        log_url)
    if m:
        (year, month, day, hour, minute, second) = [int(s) for s in m.groups()]
    else:
        dieee
        return None
    return datetime.datetime(year, month, day, hour, minute, second)
    
def get_log_urls(glider_name, ds_url='10.1.1.20'):
    index_url = 'http://%s/gmc/gliders/%s/logs/' % (ds_url, glider_name)
    u = urllib2.urlopen(index_url)
    index_str = u.read()
    log_names = sorted(set(re.findall('%s.*?\.log' % glider_name, index_str)))
    log_urls = [index_url + log_name for log_name in log_names]
    return log_urls

def get_log(log_url):
    u = urllib2.urlopen(log_url)
    log_str = u.read()
    return log_str

def get_logs(glider_name, start_date, end_date, usc_ds=True, webb_ds=False):
    # get the list of log urls from the server(s)
    log_urls = []
    if usc_ds:
        log_urls.extend(get_log_urls(glider_name, '10.1.1.20'))
    if webb_ds:
        log_urls.extend(get_log_urls(glider_name, 'expose.webbresearch.com'))

    # download each log in the given date range
    logs = {}
    for log_url in log_urls:
        date = log_date(log_url)
        if date > start_date and date < end_date:
            logs[date] = get_log(log_url)
    return logs

if __name__ == '__main__':
    import shelve, ppas
    heha_start_dt = datetime.datetime(2010,7,29, 10)
    heha_end_dt = datetime.datetime(2010, 8, 1, 3)
    rusa_start_dt = datetime.datetime(2010,7,29, 9)
    rusa_end_dt = datetime.datetime(2010, 7, 31, 0)
    start_dt = rusa_start_dt
    end_dt = rusa_end_dt
    
    # load the graph
    s = shelve.open('../runs/exp2/graphdata.dat')
    print s.keys()
    P_grg = s['P_grg']
    lm_spatial_points = s['lm_spatial_points']
    G = s['G']
    s.close()

    # plot hehape's path
    GP = ppas.pplan.GraphPlotter(G)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    GP.plot(ax, t=25)
    grg_path = path_to_positions(G, P_grg)
    heha_logs = get_logs('he-ha-pe', heha_start_dt, heha_end_dt)
    heha_locs = get_all_locations(heha_logs)
    plot_path(heha_locs, c='g')    
    plot_path(grg_path, c='r')
    ax.set_title('Path planned by GRG')
    
    # plot rusalka's path
    GP = ppas.pplan.GraphPlotter(G)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    GP.plot(ax, t=25)
    rusa_logs = get_logs('rusalka', rusa_start_dt, rusa_end_dt)
    rusa_locs = get_all_locations(rusa_logs)
    plot_path(rusa_locs, c='g')
    plot_path(lm_spatial_points, c='r')
    ax.set_title('Standard lawnmower path')
    plt.show()
