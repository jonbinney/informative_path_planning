import sys
import numpy as np
import ppas
from convenience import *

def path_to_positions(G, P):
    positions = []
    for p in P:
        positions.append(G.node_positions[p[0]])
    positions.append(G.node_positions[p[1]])
    return positions

    
def paths_to_kmlfile(filename, paths):
    elements = []
    for p_i in range(len(paths)):
        P = paths[p_i]
        el_dict = dict(
            element_type = 'path',
            name = 'Path %d' % p_i,
            description = '...',
            points = P
            )
        elements.append(el_dict)
    kml_str = ppas.kml.make_kml_str('paths', 'paths', elements)
    f = open(filename, 'w+')
    f.write(kml_str)
    f.close()

P = [(21, 18, 21, 0),
  (18, 15, 24, 0),
  (15, 16, 27, 0),
  (16, 12, 30, 0),
  (12, 16, 33, 0),
  (16, 15, 36, 0),
  (15, 12, 39, 0),
  (12, 16, 42, 0),
  (16, 19, 45, 0),
  (19, 15, 48, 0),
  (15, 12, 51, 0),
  (12, 9, 54, 0),
  (9, 8, 57, 0),
  (8, 5, 60, 0),
  (5, 1, 63, 0),
  (1, 0, 66, 0)]


G = load_var(sys.argv[1], 'G')

P_grg = path_to_positions(G, P)

# make a lawnmower path to go along with this path
lat_min, lon_min = G.node_positions[:,:2].min(axis=0)
lat_max, lon_max = G.node_positions[:,:2].max(axis=0)

roi_meters_high, roi_meters_wide = ppas.roms.degrees_to_meters(
    lat_max-lat_min, lon_max-lon_min)

lm_meters_high = (48e3 - roi_meters_wide)/4.
lm_meters_wide = roi_meters_wide/3.
lm_meters_offset = (roi_meters_high - lm_meters_high)/2.0

height_i_arr = np.array([0, 1, 1, 0, 0, 1, 1, 0])
width_i_arr = np.array([0, 0, -1, -1, -2, -2, -3, -3])
height_arr = lm_meters_high * height_i_arr + lm_meters_offset
width_arr = lm_meters_wide * width_i_arr
P_lm = []
for ii in range(len(height_arr)):
    w = width_arr[ii]
    h = height_arr[ii]
    lat_off, lon_off = ppas.roms.meters_to_degrees(h, w)
    lat = lat_off + P_grg[0][0]
    lon = lon_off + P_grg[0][1]
    P_lm.append((lat, lon))

paths_to_kmlfile('grg_path.kml', [P_grg])
paths_to_kmlfile('lm_path.kml', [P_lm])

