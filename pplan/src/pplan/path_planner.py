import threading
import numpy as np
from scipy import linalg
import ppas

class PathPlanner(threading.Thread):
    def __init__(self, out, save_store, graph_store, planner_properties):
        threading.Thread.__init__(self)
        self.daemon = True
        self.out = out
        self.save_store = save_store
        self.graph_store = graph_store
        self.planner_properties = planner_properties

    def run(self):
        self.out.set_fraction(0.01)
        self.out.writeln('Planning path')

        # create the objective class
        objective = ppas.objectives.EMSEObjective(self.graph_store['kmat'], self.planner_properties['sigma_n'])
        self.out.set_fraction(0.1)

        # plan path
        P, obj_val, obj = ppas.pplan.grg_equilateral(
            self.graph_store['G'], # graph
            self.planner_properties['start_node'], # start node
            self.planner_properties['end_node'], # end node
            self.planner_properties['start_t'], # start time
            self.planner_properties['end_t'], # end time
            self.planner_properties['max_recursions'], # recursion level
            objective, # objective function class
            self.graph_store['Xi_pilot'],
            self.planner_properties['max_recursions'])
        self.out.set_fraction(0.9)
        
        if P == None:
            self.out.writeln('Path planner failed to find a feasible path')
        else:
            self.out.writeln('Objective achieved: %f' % obj_val)
            # save result
            self.save_store['P'] = P
            self.out.set_fraction(1.0)
