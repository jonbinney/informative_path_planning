import time
import numpy as np
from scipy import linalg
import gaussian, dbg

import ppas

def grg_equilateral(
    G, # graph
    s, # start node
    t, # end node
    start_t, # start time
    end_t, # end time
    i, # recursion level
    objective, # objective function class
    Xi_pilot,
    max_recursions,
    ):
    '''
    G - dictionary representing the graph
    s - start node (int)
    t - end node (int)
    start_t - start time (int)
    end_t - end time (int)
    i - recursion level (int)
    objective - objective function class
    Xi_pilot - pilot samples (set)
    '''
    if i == max_recursions:
        dbg.printdbg('Top level')

    if G.soonest_arrival(s, t, start_t) > end_t:
        # impossible to get from node s to node t in the
        # alloted time frame
        return None, None, None

    if end_t - start_t == 0:
        # s and t must be the same node. This happens when the budget is
        # not a perfect power of 2 - we may recurse one more time than
        # necessary. Return a zero length path, and zero gain in the
        # objective function.
        return [], 0.0, objective

    # base case
    if i == 0:
        if not t in G.edge_dict[s]:
            return None, None, None
        edge_list = G.edge_dict[s][t]

        m_new_best = -np.inf
        P_best = None
        obj_best = None
        # try each edge between these nodes
        if objective.value:
            obj_without = objective.value
        else:
            obj_without = objective.f(Xi_pilot, update_dist=True)
        for e in edge_list:
            if start_t + e.length(start_t) <= end_t:
                P = [e]
                new_samples = ppas.graph.path_samples(P, start_t)
                # print 'Adding %d samples' % len(new_samples)
                samples_with = set.union(Xi_pilot, new_samples)
                obj_with = objective.f(samples_with, update_dist=True)
                m_new = obj_with - obj_without
                if m_new > m_new_best:
                    m_new_best = m_new
                    P_best = P
        return P_best, m_new_best, objective

    # recursive case
    P = None
    m = -np.inf
    obj_best = objective
    for v in G.nodes:
        # assumes edges are all equal lenghth, and time budget is
        # a power of two
        b = (start_t + end_t)/2

        if i >= max_recursions:
            spaces = '   ' * (max_recursions - i)
            dbg.printdbg(
                '%s Middle v=%d with b=%d, m=%e' % (spaces, v, b, m))

        if G.soonest_arrival(s, v, start_t) > b:
            # first half infeasible
            continue

        if G.soonest_arrival(v, t, b) > end_t:
            # second half infeasible
            continue

        #print '  '*(max_recursions - i), 'Solving first half:', list(Xi_pilot), list(objective.conditioned_on)
        P1, m1, objective_new = grg_equilateral(
            G, s, v, start_t, b, i-1, objective.copy(), Xi_pilot, max_recursions)
        if P1 == None:
            continue

        Xi_pilot_new = set.union(Xi_pilot, ppas.graph.path_samples(P1, start_t))
        #print '  '*(max_recursions - i), 'Solving second half:', list(Xi_pilot_new), list(objective_new.conditioned_on)
        P2, m2, objective_new = grg_equilateral(
            G, v, t, b, end_t, i-1, objective_new, Xi_pilot_new, max_recursions)
        if P2 == None:
            continue

        P_new = P1 + P2

        m_new = m1 + m2
        if m_new > m:
            P = P_new
            m = m_new
            obj_best = objective_new

    return P, m, obj_best

def grg_transect(
    G, # graph
    s, # start node
    t, # end node
    start_t, # start time
    end_t, # end time
    i, # recursion level
    objective, # objective function class
    Xi_pilot,
    max_recursions,
    ):
    '''
    G - dictionary representing the graph
    h - path (list) to sample (set) expansion function
    s - start node (int)
    t - end node (int)
    start_t - start time (int)
    end_t - end time (int)
    i - recursion level (int)
    objective - objective function class
    Xi_pilot - pilot samples (set)
    '''
    if i == max_recursions:
        dbg.printdbg('Top level')

    if G.soonest_arrival(s, t, start_t) > end_t:
        # impossible to get from node s to node t in the
        # alloted time frame
        return None, None

    if end_t - start_t == 0:
        # s and t must be the same node. This happens when the budget is
        # not a perfect power of 2 - we may recurse one more time than
        # necessary. Return a zero length path, and zero gain in the
        # objective function.
        return [], 0.0

    # base case
    if i == 0:
        if not t in G.edge_dict[s]:
            return None, None
        edge_list = G.edge_dict[s][t]

        m_new_best = -np.inf
        P_best = None
        obj_best = None
        # try each edge between these nodes
        obj_without = objective.f(Xi_pilot, update_dist=False)
        for e in edge_list:
            if start_t + e.length(start_t) <= end_t:
                P = [e]
                samples_with = set.union(Xi_pilot, ppas.graph.path_samples(P, start_t))
                obj_with = objective.f(samples_with, update_dist=False)
                m_new = obj_with - obj_without
                if m_new > m_new_best:
                    m_new_best = m_new
                    P_best = P
        return P_best, m_new_best

    # recursive case
    m = -np.inf
    obj_best = objective
    P = None

    b_choices = range(start_t, end_t)
    
    # always choose the middle node. assumes nodes are number 0 through n, with 0
    # always being the start node, and n always being the end node
    v = int((s + t)/2)
    
    for b in b_choices:
        if i >= max_recursions:
            spaces = '   ' * (max_recursions - i)
            dbg.printdbg(
                '%s Middle v=%d with b=%d, m=%e' % (spaces, v, b, m))

        if G.soonest_arrival(s, v, start_t) > b:
            # first half infeasible
            continue

        if G.soonest_arrival(v, t, b) > end_t:
            #second half infeasible
            continue

        P1, m1 = grg_transect(
            G, s, v, start_t, b, i-1, objective, Xi_pilot, max_recursions)
        if P1 == None:
            continue

        Xi_pilot_new = set.union(Xi_pilot, ppas.graph.path_samples(P1, start_t))
        P2, m2 = grg_transect(
            G, v, t, b, end_t, i-1, objective, Xi_pilot_new, max_recursions)
        if P2 == None:
            continue

        P_new = P1 + P2

        m_new = m1 + m2
        if m_new > m:
            P = P_new
            m = m_new

    return P, m

