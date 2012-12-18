import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import ppas

ppas.init()

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# load the graph, points, and precomputed kernel values from file
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
G = s['G']
print 'Graph type: %s' % G.graph_type
print 'Graph has %d nodes' % len(G.nodes)
points = s['points']
print 'Loaded %d points' % len(points)
Xi_pilot = s['Xi_pilot']
if planner_settings['kernel_type'] == 'gp_awe':
    print 'Using GP model with AWE kernel'
    kmat = s['gp_awe']['kmat']
elif planner_settings['kernel_type'] == 'gp_emp':
    kmat = s['Kmat']
else:
    dieeee_not_implemented
s.close()

Xi_all = set(range(len(points)))  # all possible samples

# just do the one trial and quit
if 1:
    # create the objective function class
    sigma_n = planner_settings['sigma_n']
    objective = ppas.pplan.EMSEObjective(
        kmat, sigma_n, Xi_pilot, Xi_all)

    if 1:
        P, mi, obj_best = ppas.pplan.grg(
            G,  # the graph
            planner_settings['start_node'],  # start node
            planner_settings['end_node'], # end node (last node)
            planner_settings['start_t'], # start time
            planner_settings['end_t'], # end time
            planner_settings['max_recursions'], # max number of recursions
            objective, # objective function class
            Xi_pilot,
            planner_settings['max_recursions']
            )
            
if P != None:
    s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
    s['P_grg'] = P
    s.close()
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    G.plot(ax, t=planner_settings['start_t'], nodenames=False, swap_axes=True)
    ax.scatter(points[:,1], points[:,0])
    ax.set_xticks([])
    ax.set_yticks([])
    for (v_i, v_j, start_t, edge_num) in P:
        sp_i = G.node_positions[v_i,(1,0)]
        sp_j = G.node_positions[v_j,(1,0)]
        line_artist = matplotlib.lines.Line2D(
            [sp_i[0], sp_j[0]], [sp_i[1], sp_j[1]],
            linewidth=8.0, color='red', linestyle='-')
        ax.add_artist(line_artist)
        #ppas.graph.plot_path(ax, P, points, linestyle='-',)
        plt.show()
else:
    print 'No Solution!'
