import sys, shelve, os.path
from matplotlib import pyplot as plt
import numpy as np
from scipy import linalg
import ppas

def makegraph_square_static(lat0, lon0, depth, edge_len, num_rows, num_cols):
    '''
    Construct a graph where all edges have equal lengths
    '''
    point_set = ppas.pointset.PointSet()

    # create the nodes
    nodes = []
    for lat_i in range(num_rows):
        for lon_i in range(num_cols):
            lat_off, lon_off = ppas.roms.meters_to_degrees(
                lat_i*edge_len, lon_i*edge_len)
            lat = lat0 + lat_off
            lon = lon0 + lon_off
            p = np.array((lat, lon, depth, 0.0))
            p_i = point_set.add(p)
            node = ppas.graph.Node(name=p_i, p=p, samples=set([p_i]))
            nodes.append(node)

    G = ppas.graph.Graph(nodes, graph_type='static')

    # create the edges
    for v_i in nodes:
        for v_j in nodes:
            meters_delta = ppas.roms.degrees_to_meters(
                v_i.p[0] - v_j.p[0], v_i.p[1] - v_j.p[1])
            distance = linalg.norm(meters_delta)
            if distance <= edge_len * 1.01: # fudge factor...
                if v_i != v_j:
                    edge = ppas.graph.Edge(v_i, v_j, 1.0, set())
                    G.add_edge(edge)

    return G, point_set

def makegraph_equilateral_static(
    lat0, lon0, depth, edge_len, num_rows, num_cols):
    
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

G, point_set = makegraph_square_static(
    roi_properties['lat0'],
    roi_properties['lon0'],
    roi_properties['depth'],
    graph_properties['edge_len'],
    graph_properties['shape'][0], graph_properties['shape'][1])

# save everything to a python shelf
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
s['G'] = G
s['point_set'] = point_set
s.close()


gp = ppas.plot.GraphPlotter(G)
fig = plt.figure()
ax = fig.add_subplot(111)
gp.plot(ax)
plt.show()
