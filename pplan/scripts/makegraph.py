#!/usr/bin/env python
import sys, shelve, os.path

import roslib
roslib.load_manifest('pplan')

from matplotlib import pyplot as plt
import numpy as np
from scipy import linalg
import ppas

##############################################################################
# Functions
##############################################################################

def add_point(points, p):
    '''
    Add p to points, and return the index for p
    '''
    for ii in range(len(points)):
        # hack alert! because of precision, sometimes points that should
        # be the same are actually slightly different, so we use an ugly
        # hack to get around this
        if linalg.norm(p - points[ii]) < 1e-10:
            return ii

    # point not in list yet, add it at the end
    points.append(p)
    return len(points) - 1

def makenodes_square(lat0, lat1, lon0, lon1, num_rows, num_cols):
    # create the nodes
    points = []
    lat_edgelen = np.abs(lat1 - lat0)/float(num_rows - 1)
    lon_edgelen = np.abs(lon1 - lon0)/float(num_cols - 1)
    edgelen = np.min(lat_edgelen, lon_edgelen)
    for lat in np.linspace(lat0, lat1, num_rows):
        for lon in np.linspace(lon0, lon1, num_cols):
            points.append(np.array((lat, lon)))
    return np.array(points)

def makegraph_edgetime_equilateral(data, graph_properties):
    '''
    Construct a graph where all edges have equal lengths
    '''
    graph_spatial_points = []
    nrows, ncols = graph_properties['shape']
    edge_len = graph_properties['edge_len']
    row_spacing = ppas.roms.meters_to_degrees(edge_len, 0.0)[0]
    col_spacing = ppas.roms.meters_to_degrees(
        0.0, np.cos(np.pi/6.)*edge_len)[1]
    for col_i in range(ncols):
        lon = col_i * col_spacing + roi_properties['lon0']        
        if col_i % 2 == 1:
            offset = 0.5 * row_spacing
            nrows_thiscol = nrows - 1
        else:
            offset = 0.0
            nrows_thiscol = nrows
        for row_i in range(nrows_thiscol):
            lat = offset + row_spacing * row_i + roi_properties['lat0']
            graph_spatial_points.append(np.array((lat, lon)))
    graph_spatial_points = np.array(graph_spatial_points)

    points = []
    nodes = range(len(graph_spatial_points))
    time_list = graph_properties['time_list']
    G = ppas.pplan.MultiEdgeDynamicSG(
        nodes, time_list, graph_spatial_points, 'edgetime')
    for v_i in range(len(graph_spatial_points)):
        sp_i = graph_spatial_points[v_i]
        
        for v_j in range(len(graph_spatial_points)):
            sp_j = graph_spatial_points[v_j]
            meters_delta = ppas.roms.degrees_to_meters(
                sp_i[0] - sp_j[0], sp_i[1] - sp_j[1])
            distance = linalg.norm(meters_delta)
            if distance <= edge_len * 1.01: # fudge factor...
                if v_i != v_j:
                    for t in graph_properties['time_list']:
                        if t in graph_properties['sample_time_list']:
                            samples = set()
                            ppe = graph_properties['ppe']
                            for r in np.linspace(0, 1, ppe + 2):
                                sp = (1 - r)*sp_i + r*sp_j
                                depth = roi_properties['depth']
                                p = np.array((sp[0], sp[1], depth, t))
                                p_ii = add_point(points, p)
                                samples.add(p_ii)
                        G.add_edge(v_i, v_j, t, graph_properties['edge_time'])
                        G.set_edge_samples(v_i, v_j, t, 0, samples)

    return G, np.array(points)
    
def makegraph_dynamic_roms(
    data, spatial_points, times, neighbor_distance, dive_params):
    '''
    Construct a graph where the edge lengths vary in time, and are
    determined using ROMS currents
    '''
    G = {}
    for sp_ii in range(len(spatial_points)):
        sp_i = spatial_points[sp_ii]
        G[sp_ii] = {}
        for sp_jj in range(len(spatial_points)):
            sp_j = spatial_points[sp_jj]
            if sp_ii != sp_jj:
                if linalg.norm(sp_i - sp_j) < neighbor_distance:
                    for t in times:
                        G[sp_ii][(sp_jj, t)] = ppas.roms.glider_travel_time(
                            data, t, sp_i, sp_j, dive_params)
    return G

def makegraph_transect_dynamic_roms(
    data, lat0, lon0, lat1, lon1, num_nodes, depth_list, time_list):
    
    spatial_points = []
    points = []
    
    # choose the spatial points
    sp0 = np.array((lat0, lon0))
    sp1 = np.array((lat1, lon1))
    for r in np.linspace(0, 1, num_nodes):
        sp = (1-r)*sp0 + r*sp1
        spatial_points.append(sp)

    # duplicate the points, in order to build a graph that allows
    # travel in only one direction out and back
    spatial_points = spatial_points + spatial_points[-2::-1]

    # make the graph
    nodes = range(len(spatial_points))
    G = ppas.graph.Graph(nodes, 'depth_transect')

    # add edges
    for v_i in range(len(spatial_points) - 1):
        v_j = v_i + 1
        for d in depth_list:        
            length_dict = {}
            sample_dict = {}
            for t in time_list:
                sp_i = spatial_points[v_i]
                sp_j = spatial_points[v_j]

                dive_params = dict(
                    dive_spacing = 100.,
                    min_depth = d, # minimum glider depth in meters
                    max_depth = d, # maximum glider depth in meters
                    horizontal_vel = .278 # glider velocity in m/s
                    )
                
                edge_seconds = ppas.roms.glider_travel_time(
                    data, t, sp_i, sp_j, dive_params)

                edge_minutes = edge_seconds/60.
                edge_len = int(edge_minutes/60)
                
                #edge_num = G.add_edge(v_i, v_j, t, edge_len)
                length_dict[t] = edge_len
                
                # add test points
                sp = (sp_i + sp_j) / 2.
                p = np.array((sp[0], sp[1], d, t))
                p_i = add_point(points, p)

                # update edge to sample mapping
                sample_dict[t] = set([p_i])
                #G.set_edge_samples(v_i, v_j, t, edge_num, set([p_i]))
            e = ppas.graph.DiscreteTimeEdge(v_i, v_j, length_dict, sample_dict)
            e.info = {'depth': d}
            G.add_edge(e)

    # add a loopback edge at the last node, so that the path can complete
    # early
    v_end = len(spatial_points) - 1
    sample_dict = {}
    length_dict = {}
    for t in time_list:
        sample_dict[t] = set()
        length_dict[t] = 1
    e = ppas.graph.DiscreteTimeEdge(v_end, v_end, length_dict, sample_dict)
    G.add_edge(e)
    # edge_num = G.add_edge(v_end, v_end, t, edge_len=1)
    
    return G, np.array(spatial_points), np.array(points)

def edgetime_points(
    G, graph_spatial_points, graph_ppe, graph_timesteps, points_list):
    hdict = {}

    for v_i in G:
        sp_i = graph_spatial_points[v_i]
        for v_j in G[v_i]:    
            sp_j = graph_spatial_points[v_j]
            rlist = np.linspace(0, 1, graph_ppe+2)
            for t in graph_timesteps:
                hdict[(v_i, v_j, t)] = set()
                for r in rlist:
                    sp = (1-r)*sp_i + r*sp_j
                    p = np.concatenate((sp, np.array((t,))))
                    p_i = add_point(points_list, p)
                    hdict[(v_i, v_j, t)].add(p_i)
                    
    expander = ppas.pplan.EdgeTimeExpander(hdict)
    return expander

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

# load the ROMS data
s = shelve.open(os.path.join(run_dir, 'romsdata.dat'))
data = s['data']
s.close()

s = shelve.open(os.path.join(run_dir, 'data.shelf'))

if mode == 'edgetime' and graph_properties['graph_type'] == 'equilateral':
    # each cell in the grid is 2x2km
    # leave a 10% border around the AOI for aesthetic reasons
    
    # create the graph
    G, points = makegraph_edgetime_equilateral(
        data, graph_properties)

elif mode == 'depth_transect':
    num_nodes = graph_properties['num_nodes']
    depth_list = graph_properties['depth_list']
    time_list = graph_properties['time_list']
    G, graph_spatial_points, points = makegraph_transect_dynamic_roms(
        data, lat_start, lon_start, lat_end, lon_end, num_nodes, depth_list,
        time_list)
    s['graph_spatial_points'] = graph_spatial_points

# no pilot data for now
Xi_pilot = set()

# save everything to a python shelf
s['G'] = G
s['points'] = points
s['Xi_pilot'] = Xi_pilot
s.close()
