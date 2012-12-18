import sys, time, shelve, os.path, copy
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import pyplot as plt
import ppas.bnb

class BranchAndBoundMulti:
    def __init__(self, G, objective, reachable_cache, pilot_samples, args):
        self.G = G
        self.pilot_samples = pilot_samples
        self.objective = objective
        self.reachable_cache = reachable_cache
        self.pilot_samples = pilot_samples
        self.args = args

    def plan(self):
        return self.plan_sequential()

    def plan_sequential(self):
        results = {}
        results['intermediate_paths'] = []
        results['cumulative_evals'] = []
        paths = [[] for ii in range(len(self.args['robots']))]
        lower_bound = -np.inf
        for replan_i in range(self.args['replans']+1):
            for robot_i, robot in enumerate(self.args['robots']):
                cumulative_evals = []
                print 'Replan %d, robot %d, num_evals=%d' % (replan_i, robot_i,
                    self.objective.num_evaluations)
                samples_so_far = self.pilot_samples.copy()
                for P_i, P in enumerate(paths):
                    if not P_i == robot_i:
                        samples_so_far.update(ppas.graph.path_samples(P))

                # create new bnb planner (and seed with current lower bound)
                bnb_planner = ppas.bnb.BranchAndBound(self.G, samples_so_far,  self.objective,
                    self.reachable_cache, self.args['use_bnb'], self.args['use_smart_order'],
                    bound_scaling=self.args['bound_scaling'], initial_lower_bound=lower_bound)

                # plan path for this robot
                P, obj_val = bnb_planner.plan_with_horizon(robot['v_start'], robot['v_end'],
                    robot['t_start'], robot['t_end'], horizon=self.args['horizon'])

                # update plan for this robot
                paths[robot_i] = P
                cumulative_evals.append(self.objective.num_evaluations)

                # update the lower bound. we use the lower bound from this plan
                # the lower bound for the next replan
                lower_bound = bnb_planner.lower_bound
            results['intermediate_paths'].append(copy.deepcopy(paths))
            results['cumulative_evals'].append(cumulative_evals)
        results['paths'] = paths
        return results
