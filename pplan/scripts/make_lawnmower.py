import sys
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

G = load_var(sys.argv[1], 'G')
paths_to_kmlfile('paths.kml', [path_to_positions(G, P)])
