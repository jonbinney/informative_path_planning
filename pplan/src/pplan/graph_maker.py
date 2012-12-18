import threading
import numpy as np
from scipy import linalg
import ppas

class GraphMaker(threading.Thread):
    def __init__(self, out, save_store, roi_properties, graph_properties):
        threading.Thread.__init__(self)
        self.daemon = True
        self.out = out
        self.save_store = save_store
        self.roi_properties = roi_properties
        self.graph_properties = graph_properties

    def run(self):
        self.out.set_fraction(0.01)
        self.out.writeln('Making graph')
        G, points = makegraph_edgetime_equilateral(self.roi_properties, self.graph_properties)
        G.cache_soonest_arrivals(self.graph_properties['time_list'])
        self.out.writeln('Saving graph')
        self.out.set_fraction(0.9)
        self.save_store['G'] = G
        self.save_store['points'] = points
        self.save_store['Xi_pilot'] = set()
        self.out.set_fraction(1.0)

