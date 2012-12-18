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
        

def makegraph_edgetime_equilateral(roi_properties, graph_properties):
    '''
    Construct a graph where all edges have equal lengths
    '''

    spatial_points = []
    nrows, ncols = graph_properties['shape']
    edge_distance = graph_properties['edge_distance']
    row_spacing = ppas.roms.meters_to_degrees(edge_distance, 0.0)[0]
    col_spacing = ppas.roms.meters_to_degrees(
        0.0, np.cos(np.pi/6.)*edge_distance)[1]
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
    G = ppas.graph.Graph(nodes, 'discrete_time')
    G.node_points = spatial_points

    starttime = ppas.datetime_to_seconds(roi_properties['starttime'])

    points = []
    for v_i in nodes:
        sp_i = spatial_points[v_i]
        for v_j in nodes:
            sp_j = spatial_points[v_j]
            meters_delta = ppas.roms.degrees_to_meters(
                sp_i[0] - sp_j[0], sp_i[1] - sp_j[1])
            distance = linalg.norm(meters_delta)
            if distance <= edge_distance * 1.01 and v_i != v_j: # fudge factor...
                length_dict = {}
                sample_dict = {}
                for t in graph_properties['time_list']:
                    length_dict[t] = graph_properties['edge_len']
                    samples = set()
                    ppe = graph_properties['ppe']

                    # technically each sample should be at a different time, but
                    # then we would end up with more points (due to points being
                    # at different times depending on which direction the edge
                    # is taversed)
                    t_s = 0.5 * t + 0.5 * (t + graph_properties['edge_len'])
                    for r in np.linspace(0., 1., ppe):
                        sp = (1 - r)*sp_i + r*sp_j
                        depth = roi_properties['depth']
                        
                        p = np.array((sp[0], sp[1], depth, t_s))
                        p_ii = add_point(points, p)
                        samples.add(p_ii)
                    sample_dict[t] = samples
                e = ppas.graph.DiscreteTimeEdge(v_i, v_j, length_dict, sample_dict)
                G.add_edge(e)
    return G, np.array(points)


                 
