import numpy as np

class Node:
    def __init__(self, name=None, x=None, samples=set()):
        self.name = name
        self.x = x
        self._samples = samples

    def samples(self):
        return self._samples

class Edge:
    def __init__(self, v_i, v_j, length, samples=set()):
        self.v_i = v_i
        self.v_j = v_j
        self._length = length
        self._samples = samples
        
    def length(self, t=0):
        return self._length

    def samples(self, t=0):
        return self._samples

class DiscreteTimeEdge(Edge):
    def __init__(self, v_i, v_j, length_dict, sample_dict=None):
        self.v_i = v_i
        self.v_j = v_j
        self._length_dict = length_dict
        self._sample_dict = sample_dict

    def length(self, t):
        if t in self._length_dict:
            return self._length_dict[t]
        else:
            return np.inf

    def samples(self, t):
        return self._sample_dict[t]

class Graph:
    '''
    A general graph class. By using different edge classes, can
    represent static or time-varying graphs. Allows multiple edges
    between a pair of nodes.
    '''
    def __init__(self, nodes, graph_type='static'):
        self.nodes = set(nodes)
        self.graph_type = graph_type
        self.edge_dict = dict([(v_i, {}) for v_i in self.nodes])
        self.L = None

    def add_node(self, v):
        self.nodes.add(v)
        self.edge_dict[v] = {}
        return v

    def add_edge(self, edge):
        ''' Add the edge to the graph '''
        if edge.v_j in self.edge_dict[edge.v_i]:
            self.edge_dict[edge.v_i][edge.v_j].append(edge)
        else:
            self.edge_dict[edge.v_i][edge.v_j] = [edge]            

    def neighbors(self, v_i):
        return set(self.edge_dict[v_i].keys())

    def node_edges(self, v_i):
        edges = []
        for edge_list in self.edge_dict[v_i].values():
            edges.extend(edge_list)
        return set(edges)

    def soonest_arrival(self, v_i, v_j, t_start=0):
        if self.graph_type == 'static':
            return t_start + self.L[v_i][v_j]
        elif self.graph_type == 'discrete_time':        
            return self.L[(v_i, t_start)][v_j]
        
    def cache_soonest_arrivals(self, time_list=None):
        if self.graph_type == 'static':
            self.L = {}
            for v_i in self.nodes:
                dists, prev = djikstra(self, v_i)
                self.L[v_i] = dists
        elif self.graph_type == 'discrete_time':
            self.L = {}
            for v_i in self.nodes:
                for t in time_list:
                    self.L[(v_i, t)] = dynamic_djikstra(self, v_i, t)
        else:
            diee_unknown_graph_type___

def path_samples(P, t_start=None):
    if t_start == None:
        samples = set()
        for e in P:
            samples = samples.union(e.samples())
    else:
        # time varying
        t = t_start
        samples = set()
        for e in P:
            samples = samples.union(e.samples(t))
            t += e.length(t)
    return samples

def path_length(P, t_start=None):
    if t_start == None:
        return np.sum([e.length() for e in P])
    else:
        # time varying
        t = t_start
        for e in P:
            t += e.length(t)
        return t

def dynamic_djikstra(G, v_i, t_start):
    # djikstra adapted for time-varying edge lengths
    arrival_time = {}
    previous = {}
    for v in G.nodes:
        arrival_time[v] = np.inf                
        previous[v] = None

    # set start node
    arrival_time[v_i] = t_start
    
    Q = G.nodes.copy()
    while len(Q) > 0:
        soonest_arrival_time = np.inf
        u = None
        for v in Q:
            if arrival_time[v] < soonest_arrival_time:
                soonest_arrival_time = arrival_time[v]
                u = v
        if u == None:
            break
        Q.remove(u)
        t = arrival_time[u]
        
        for v in G.nodes:
            if v in Q:
                if v in G.edge_dict[u]:
                    e = G.edge_dict[u][v]
                    edge_len = np.min(
                        [e.length(arrival_time[u]) for e in G.edge_dict[u][v]])
                    alt = arrival_time[u] + edge_len
                    if alt < arrival_time[v]:
                        arrival_time[v] = alt
                        previous[v] = u
    return arrival_time

def djikstra(G, s):
    # from the pseudocode at:
    #   http://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
    dist = {}
    previous = {}
    for v in G.nodes:
        dist[v] = np.inf
        previous[v] = None

    dist[s] = 0
    Q = G.nodes.copy()
    while len(Q) > 0:
        u = min(Q, key=dist.get)
        if dist[u] == np.inf:
            break
        Q.remove(u)
        for v in G.neighbors(u):
            if v in Q:
                alt = np.min([(dist[u] + e.length()) for e in G.edge_dict[u][v]])
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = u
    return dist, previous

def all_shortest_paths(G):
    # build dictionary of the shortest path distances between various nodes
    L = {}
    for v in G.nodes:
        (dist, previous) = djikstra(G, v)
        L[v] = dist
    return L
