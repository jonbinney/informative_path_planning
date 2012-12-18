import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import ppas

def modhist_ubound(G, v_start, v_end, t_start, t_end, Xi_pilot, objective, L):
    '''
    Note: Only works for edge lengths of 1
    '''
    d_dict = {}
    value_pilot = objective.f(Xi_pilot)
    value_start = objective.f(set.union(Xi_pilot, s.samples()))
    d_dict[t_start]= {v_start: value_start - value_pilot}

    timesteps = range(t_start, t_end+1)
    for t, t_next in zip(timesteps[:-1], timesteps[1:]):
        d_dict[t_next] = {}
        for v_i in d_dict[t]:
            Xi_before = set.union(Xi_pilot, v_i.samples())
            value_before = objective.f(Xi_before)
            for v_j in G.neighbors(v_i):
                Xi_after = set.union(Xi_pilot, v_i.samples(), v_j.samples())
                value_after = objective.f(Xi_after)
                node_gain = value_after - value_before
                new_value = d_dict[t][v_i] + node_gain
                if (not v_j in d_dict[t_next]
                    or new_value > d_dict[t_next][v_j]):
                    d_dict[t_next][v_j] = new_value
    return d_dict[t_end][v_end]
    
def greedy(G, s, t, start_t, end_t, Xi_pilot, objective):
    '''
    NOTE - Currently makes sense only for graphs where all edges have
    equal length, because it greedily chooses the best next edge based
    on objective value, ignoring length
    '''
    # create shortest path dictionary
    L = ppas.graph.all_shortest_paths(G)
    
    P = []
    current_node = s
    # build path iteratively
    for tau in range(start_t, end_t):
        # try all neighboring nodes
        best_edge = None
        best_val = -np.inf
        for e in G.node_edges(current_node):
            # make sure we can still get to the end node
            if e.length() + L[e.v_j][t] <= end_t-tau:
                Xi_path = ppas.graph.path_samples(P + [e])
                new_val = objective.f(set.union(Xi_pilot, Xi_path))
                if new_val > best_val:
                    best_edge = e
                    best_val = new_val
        P.append(best_edge)
        current_node = best_edge.v_j
    return P

def nodes_to_path(node_list):
    path = []
    for ii in range(len(node_list) - 1):
        v = node_list[ii]
        v_next = node_list[ii+1]
        e = G.edge_dict[v][v_next]
        path.append(e)
    return path

def reachable_nodes(G, L, R, fixed_nodes):
    reachable = set()
    for ii in range(len(fixed_nodes)-1):
        v_i = fixed_nodes[ii]
        if v_i != None:
            # find the next fixed node
            jj = ii + 1
            while fixed_nodes[jj] == None:
                jj += 1

            v_j = fixed_nodes[jj]
            reachable.update( R[(v_i, v_j, jj-ii)] )
    return reachable

def binary_order(n_start, n_end):
    if n_start == n_end:
        return [n_start]
    elif n_end - n_start == 1:
        return [n_start, n_end]
    else:
        n_middle = int(np.floor((n_start + n_end)/2.0))
        first_half = binary_order(n_start, n_middle - 1)
        second_half = binary_order(n_middle + 1, n_end)
        return [n_middle] + first_half + second_half

class BranchAndBound:
    def __init__(self, G, Xi_pilot, objective, reachable_cache, use_bnb=True, use_smart_order=False, bound_scaling=1.0, initial_lower_bound=-np.inf):
        self.G = G
        self.Xi_pilot = Xi_pilot
        self.objective = objective
        self.reachable_cache = reachable_cache
        self.use_bnb = use_bnb
        self.use_smart_order = use_smart_order     
        self.bound_scaling = bound_scaling
        self.lower_bound = initial_lower_bound
        self.num_calls = 0

    def upper_bound(self, v_start, v_end, t_start, t_end, Xi_sofar):
        reachable_set = self.reachable_cache[(v_start, v_end, np.ceil(t_end-t_start))]
        return self.objective.f(set.union(Xi_sofar, reachable_set))

    def plan_with_horizon(self, v_start, v_end, t_start, t_end, horizon):
        if horizon < 1:
            die_bad_horizon__
        path_sofar = []
        v = v_start
        t = t_start
        while t < t_end:
            self.lower_bound = -np.inf
            print t_start, t_end, t, v_start, v_end, v
            samples_sofar = ppas.graph.path_samples(path_sofar, t_start)
            P, val = self.plan(v, v_end, t, t_end, samples_sofar, horizon)
            if len(P) < horizon or ppas.graph.path_length(path_sofar+P, t_start) == t_end:
                path_sofar += P
                break
            e = P[0]
            t += e.length(t)
            path_sofar.append(e)
            v = e.v_j
        if path_sofar[-1].v_j != v_end:
            die_wrong_end_vertex____

        return path_sofar, val

    def plan(self, v_start, v_end, t_start, t_end, Xi_path=set(), horizon=np.inf):
        self.num_calls += 1

        # are we done?
        if horizon == 0:
            Xi_sofar = set.union(self.Xi_pilot, Xi_path)
            return [], self.objective.f(Xi_sofar)

        # calculate upper bounds
        upper_bounds = {}
        for e in list(self.G.node_edges(v_start)):
            # is it possible?
            if float(self.G.soonest_arrival(e.v_j, v_end, t_start+e.length(t_start))) > t_end:
                continue

            if self.use_bnb:
                Xi_sofar = set.union(self.Xi_pilot, Xi_path, ppas.graph.path_samples([e], t_start))
                ub = self.upper_bound(e.v_j, v_end, t_start+e.length(t_start), t_end, Xi_sofar)
                upper_bounds[e] = ub
            else:
                upper_bounds[e] = np.inf

        if self.use_smart_order:
            ordered_edges = sorted(upper_bounds, key=upper_bounds.get, reverse=True)
        else:
            ordered_edges = list(upper_bounds.keys())
        
        # recursively try each outgoing edge
        Xi_sofar = set.union(self.Xi_pilot, Xi_path)
        if v_start == v_end and t_start <= t_end:
            best_value = self.objective.f(Xi_sofar)
            best_path = []
        else:
            best_value = -np.inf
            best_path = None
        for e in ordered_edges:
            if upper_bounds[e] <= self.bound_scaling*self.lower_bound:
                continue

            # recursively try this edge
            Xi_edge = e.samples(t_start)
            remaining_path, value = self.plan(e.v_j, v_end, t_start+e.length(t_start),
                t_end, set.union(self.Xi_pilot, Xi_path, Xi_edge), horizon-1)
        
            if remaining_path != None and value > best_value:
                best_path = [e] + remaining_path
                best_value = value

            if value > self.lower_bound:
                self.lower_bound = value

        return best_path, best_value
