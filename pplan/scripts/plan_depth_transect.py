import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import roslib
roslib.load_manifest('pplan')
import ppas

ppas.init()

Xi_all = set(range(len(points)))

# create the objective function class
sigma_n = hyper_params[0]
objective = ppas.objectives.EMSEObjective(
    Kmat, sigma_n, Xi_pilot, Xi_all)

max_recursions = int(np.ceil(np.log2(len(G.nodes)-1)))
print 'Max number of recursions is', max_recursions

# cache shortest path lengths for all node pairs and start times
print 'Caching shortest path lengths'
time_list = set(points[:,-1])
G.cache_soonest_arrivals(time_list)

def all_paths(G, v, horizon):
    if horizon == 0:
        return [[]]

    paths = []
    remaining_paths = all_paths(G, v+1, horizon-1)
    for e in G.edge_dict[v][v+1]:
        for P in remaining_paths:
            paths.append([e] + P)
            
    return paths

def greedyn_transect(G, t_start, t_end, objective, Xi_pilot, horizon):
    P = []
    t = t_start
    v = 0
    v_end = len(G.nodes) - 1
    for v in range(v_end - horizon + 1):
        best_objval = -np.inf
        best_subpath = None
        for subpath in all_paths(G, v, horizon):
            t_new = ppas.graph.path_length(subpath, t)
            if t_new > t_end or G.soonest_arrival(subpath[-1].v_j, v_end, t_new) > t_end:
                continue
            
            samples = ppas.graph.path_samples(P+subpath, 0)
            objval = objective.f(samples, update_dist=False)
            if objval > best_objval:
                best_objval = objval
                best_subpath = subpath
        # only add the next node, then replan
        P.append(best_subpath[0])
        t = best_subpath[0].length(t)
    P.extend(best_subpath[1:])
    return P


B = B_list[0]
if 0:
    print 'Planning transect using grg_transect'
    P, obj_val = ppas.pplan.grg_transect(
        G,  # the graph
        0,  # start node
        max(G.nodes), # end node (last node)
        0, # start time
        23, # end time
        max_recursions, # max number of recursions
        objective, # objective function class
        Xi_pilot,
        max_recursions # used to tell when at top level of recursion
        )
else:
    horizon_list = range(1, 4)
    objval_list = []
    length_list = []
    for horizon in horizon_list:
        ppas.dbg.printdbg('Planning transect using greedy, horizon=%d' % horizon)
        P = greedyn_transect(
            G = G,
            t_start = 0,
            t_end = 23,
            objective = objective,
            Xi_pilot = Xi_pilot,
            horizon=horizon)
        objval = objective.f(ppas.graph.path_samples(P, 0), update_dist=False)
        objval_list.append(-objval)
        length_list.append(ppas.graph.path_length(P, 0))
    plt.figure()
    plt.plot(horizon_list, objval_list)
    plt.figure()
    plt.plot(horizon_list, length_list)
    plt.show()
