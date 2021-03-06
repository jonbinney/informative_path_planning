import numpy as np
from scipy import linalg
import ppas

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
        
def makegraph_static_equilateral(roi_properties, graph_properties):
    '''
    Construct a static graph where all edges have equal lengths.
    '''

    spatial_points = []
    nrows, ncols = graph_properties['shape']
    edge_distance = graph_properties['edge_distance']
    row_spacing = edge_distance
    col_spacing = np.cos(np.pi/6.)*edge_distance
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
            spatial_points.append(np.array((lat, lon)))
    spatial_points = np.array(spatial_points)

    # make the graph
    nodes = range(len(spatial_points))
    G = ppas.graph.Graph(nodes, graph_type='static')
    G.node_points = spatial_points

    points = []
    for v_i in nodes:
        sp_i = spatial_points[v_i]
        for v_j in nodes:
            sp_j = spatial_points[v_j]
            distance = linalg.norm(sp_i-sp_j)
            if distance <= edge_distance * 1.01 and v_i != v_j: # fudge factor...
                samples = set()
                ppe = graph_properties['ppe']
                for r in np.linspace(0., 1., ppe):
                    sp = (1 - r)*sp_i + r*sp_j
                    p_ii = add_point(points, sp)
                    samples.add(p_ii)
                e = ppas.graph.Edge(v_i, v_j, graph_properties['edge_len'], samples)
                G.add_edge(e)
    return G, np.array(points)


                 
