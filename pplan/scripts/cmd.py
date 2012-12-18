#!/usr/bin/env python
import roslib
roslib.load_manifest('pplan')
import sys, time, os, os.path, multiprocessing, datetime, signal
import numpy as np

import pplan, ppas

class PPlanCMD:
    def __init__(self, num_processes):
        self.num_processes = num_processes
        run_path = sys.argv[1]
        if os.path.isfile(run_path):
            # file contains list of running directories
            loc = {}
            execfile(run_path, {}, loc)
            self.commands = loc['commands']
            self.run_dirs = loc['run_dirs']
        else:
            self.commands = sys.argv[2:]            
            self.run_dirs = [run_path]
        self.command_to_func = {
            'get_data' : get_data,
            'make_graph' : make_graph,
            'calc_cov' : calc_cov,
            'calc_emp_cov' : calc_emp_cov,
            'plan_path_grg' : plan_path_grg,
            'plan_path_bnb' : plan_path_bnb,
            'plan_path_bnbmulti' : plan_path_bnbmulti,
            'plan_path_bruteforce' : plan_path_bruteforce,
            'compute_reachable_cache' : compute_reachable_cache,
            'make_ma' : make_ma,
            'calc_emse' : calc_emse,
            'dummy' : dummy
            }

    def run(self):
        if self.num_processes > 1:
            print 'Spawning %d worker processes' % self.num_processes
            pool = multiprocessing.Pool(self.num_processes, init_worker)
        for cmd, args in self.commands:
            self.run_on_dirs(cmd, args)

    def run_on_dirs(self, cmd, args):
        func = self.command_to_func[cmd]
        if self.num_processes == 1:
            for run_dir in self.run_dirs:
                func(run_dir, args)
        else:
            try:
                res = pool.map_async(func, self.run_dirs, args)
                while not res.ready():
                    time.sleep(0.01)
            except KeyboardInterrupt:
                print "Caught KeyboardInterrupt, terminating workers"
                pool.terminate()
                pool.join()
                return

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def get_data(run_dir):
    print '%s: getting data' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)

    rp = settings.roi_properties
    dates = settings.training_properties['dates']
    for date_i in range(len(dates)):
        date = dates[date_i]
        try:
            # connect to ROMS
            dset = ppas.roms.open_dataset(date)
            
            # get the data
            data = ppas.roms.get_data(
                dset, rp['lat0']-0.03, rp['lat1']+0.03, rp['lon0']-0.03, rp['lon1']+0.03,
                rp['depth']-10., rp['depth']+10.)

            store['training_data/' + str(date)] = data
        except Exception, e:
            print 'No ROMS data available for %s' % str(date)
            print e
        print '%s: Downloaded data for %s (%d/%d)' % (run_dir, str(date), date_i+1, len(dates))
        time.sleep(0.1)

def make_graph(run_dir, args):
    global pplan
    print '%s: making graph' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)
    graph_type = settings.graph_properties['graph_type']
    if graph_type == 'edgetime_equilateral':
        import pplan.makegraph_edgetime_equilateral
        G, points = pplan.makegraph_edgetime_equilateral.makegraph_edgetime_equilateral(
            settings.roi_properties, settings.graph_properties)
    elif graph_type == 'static_equilateral':
        import pplan.makegraph_static_equilateral
        G, points = pplan.makegraph_static_equilateral.makegraph_static_equilateral(
            settings.roi_properties, settings.graph_properties)
    else:
        crash_bad_graph_type_

    G.cache_soonest_arrivals(settings.graph_properties['time_list'])
    store['G'] = G
    store['points'] = points
    store['Xi_pilot'] = set()

def plan_path_grg(run_dir, args):
    print '%s: planning path using GRG' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)

    # create the objective class
    objective = ppas.objectives.EMSEObjective(store['kmat'], settings.planner_properties['sigma_n'])
    obj_val0 = objective.f(set())
    
    # plan path
    t0 = time.time()
    P, obj_val, obj = ppas.pplan.grg_equilateral(
        store['G'], # graph
        settings.planner_properties['start_node'], # start node
        settings.planner_properties['end_node'], # end node
        settings.planner_properties['start_t'], # start time
        settings.planner_properties['end_t'], # end time
        settings.planner_properties['max_recursions'], # recursion level
        objective, # objective function class
        store['Xi_pilot'],
        settings.planner_properties['max_recursions'])
    runtime = time.time() - t0

    result = {
        'P' : P,
        'obj_val' : -(-obj_val0 - obj_val), # convert reduction in EMSE to -EMSE
        'obj_val0' : obj_val0,
        'objective_function' : 'emse',
        'runtime' : runtime
        }
    save_result(store, 'grg', args, result)
        
    if P == None:
        print '%s: Path planner failed to find a feasible path' % run_dir
    else:
        print '%s: Objective achieved by path: %f' % (run_dir, obj_val)
        # save result
        store['P'] = P

def plan_path_bnb(run_dir, args):
    print '%s: planning path using bnb' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)

    # create the objective class
    objective = ppas.objectives.EMSEObjective(store['kmat'], settings.planner_properties['sigma_n'])
    obj_val0 = objective.f(set())
    
    bnb_planner = ppas.bnb.BranchAndBound(
        store['G'],
        store['Xi_pilot'],
        objective,
        reachable_cache=store['reachable_cache'],
        use_bnb=True,
        use_smart_order=False
        )

    print 'BNB planning path from %d to %d' % ( 
        settings.planner_properties['start_node'],
        settings.planner_properties['end_node'])

    t0 = time.time()
    P, obj_val = bnb_planner.plan_with_horizon(
        settings.planner_properties['start_node'],
        settings.planner_properties['end_node'],
        settings.planner_properties['start_t'],
        settings.planner_properties['end_t'],
        horizon=args['horizon']
        )
    runtime = time.time() - t0

    result = {
        'P' : P,
        'obj_val' : obj_val,
        'obj_val0' : obj_val0,
        'objective_function' : 'emse',
        'runtime' : runtime
        }
    save_result(store, 'bnb', args, result)
    
    if P == None:
        print '%s: Path planner failed to find a feasible path' % run_dir
    else:
        print '%s: Objective achieved by path: %f' % (run_dir, obj_val)
        print P[0].v_i, P[-1].v_j

def plan_path_bnbmulti(run_dir, args):
    print '%s: planning path using bnb multi' % run_dir
    print args
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)

    G = store['G']
    reachable_cache = store['reachable_cache']

    # create the objective class
    objective = ppas.objectives.EMSEObjective(store['kmat'], settings.planner_properties['sigma_n'])
    obj_val0 = objective.f(set())
    
    # create the planner
    bnb_multi_planner = ppas.bnb_multi.BranchAndBoundMulti(
        G,
        pilot_samples = set(),
        objective = objective,
        reachable_cache = reachable_cache,
        args = args,
        )

    t0 = time.time()
    planner_result = bnb_multi_planner.plan()
    paths = planner_result['paths']
    runtime = time.time() - t0

    obj_val = objective.f(set.union(*[ppas.graph.path_samples(P) for P in paths]))

    result = {
        'paths' : paths,
        'planner_result' : planner_result,
        'obj_val' : obj_val,
        'obj_val0' : obj_val0,
        'objective_function' : 'emse',
        'runtime' : runtime,
        'objfunc_evals' : objective.num_evaluations
        }
    save_result(store, 'bnb_multi', args, result)
    
    if P == None:
        print '%s: Path planner failed to find a feasible path' % run_dir
    else:
        print '%s: Objective achieved by path: %f' % (run_dir, obj_val)
        print P[0].v_i, P[-1].v_j

def save_result(store, algorithm, args, result):
    dirnum = 0
    while True:
        base_key = os.path.join('results', '%d' % dirnum)
        if len(store.keys(base_key)) == 0:
            break 
        dirnum += 1
    print 'Saving result in %s' % base_key
    store[os.path.join(base_key, 'algorithm')] = algorithm
    store[os.path.join(base_key, 'args')] = args
    store[os.path.join(base_key, 'result')] = result

def plan_path_bruteforce(run_dir, args):
    print '%s: planning path using brute force' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)

    # create the objective class
    objective = ppas.objectives.EMSEObjective(store['kmat'], settings.planner_properties['sigma_n'])
    obj_val0 = objective.f(set())
    
    bnb_planner = ppas.bnb.BranchAndBound(
        store['G'],
        store['Xi_pilot'],
        objective,
        reachable_cache=None,
        use_bnb=False,
        use_smart_order=False
        )

    print 'BF planning path from %d to %d' % ( 
        settings.planner_properties['start_node'],
        settings.planner_properties['end_node'])

    t0 = time.time()
    P, obj_val = bnb_planner.plan_with_horizon(
        settings.planner_properties['start_node'],
        settings.planner_properties['end_node'],
        settings.planner_properties['start_t'],
        settings.planner_properties['end_t'],
        horizon=args['horizon']
        )
    runtime = time.time() - t0

    result = {
        'P' : P,
        'obj_val' : obj_val,
        'obj_val0' : obj_val0,
        'objective_function' : 'emse',
        'runtime' : runtime
        }
    save_result(store, 'bruteforce', args, result)
    
    if P == None:
        print '%s: Path planner failed to find a feasible path' % run_dir
    else:
        print '%s: Objective achieved by path: %f' % (run_dir, obj_val)
        print P[0].v_i, P[-1].v_j

def calc_cov(run_dir, args):
    print '%s: calculating empirical covariance matrix' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)
    if settings.training_properties['kernel_type'] == 'weighted_rbf':
        kernel = ppas.gp.kernels.WeightedRBF()
    elif settings.training_properties['kernel_type'] == 'rbf':
        kernel = ppas.gp.kernels.RBF()
    else:
        diee_unknown_kernel_type___
    
    points = store['points']
    kmat = kernel.value(settings.training_properties['hyper_params'], points, points)
    store['kmat'] = kmat
            

def calc_emp_cov(run_dir, args):
    print '%s: calculating empirical covariance matrix' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)
    training_store = ppas.Store(os.path.join(settings.data_dir, 'training_data'))
    
    points = store['points']
    qoi = settings.roi_properties['qoi']
    training_dates = sorted(training_store.keys())
    training_array = np.zeros((len(points), len(training_dates)))

    exp_start = settings.roi_properties['starttime']
    exp_midnight = datetime.datetime(exp_start.year, exp_start.month, exp_start.day, 0, 0)
    
    # build array of training data
    for date_i in range(len(training_dates)):
        date_str = training_dates[date_i]
        data = training_store[date_str]
        data_year, data_month, data_day = [int(s) for s in date_str.split('-')]
        data_midnight = datetime.datetime(data_year, data_month, data_day, 0, 0)
        if exp_start.hour < 13:
            exp_midnight += datetime.timedelta(days=1)
        time_offset = ppas.datetime_to_seconds(exp_midnight) - ppas.datetime_to_seconds(data_midnight)
        for p_i in range(len(points)):
            p = points[p_i]
            t = p[3] - time_offset
            val = ppas.roms.get_value(data, p[0], p[1], p[2], t, qoi, interp='linear')
            training_array[p_i,date_i] = val

    # filter out bad data
    if qoi == 'salt':
        varmin, varmax = 30., 40.
    elif qoi == 'temp':
        varmin, varmax = 0., 100.
    else:
        dieee_unknown_var_type___
    good_columns = ((training_array > varmin) & ( training_array < varmax)).all(axis=0)
    good_training_data = training_array[:,good_columns]
    store['good_training_data'] = good_training_data

    # calculate covariance matrix
    kmat = np.cov(good_training_data)
    store['kmat'] = kmat

def compute_reachable_cache(run_dir, args):
    print '%s: calculating reachable cache' % run_dir
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)

    t_max = args['t_max']

    G = store['G']
    G.cache_soonest_arrivals()

    all_edges = set()
    for v_i in G.nodes:
        for v_j in G.edge_dict[v_i]:
            all_edges.update(G.edge_dict[v_i][v_j])

    reachable_cache = {}
    for v_i in G.nodes:
        print v_i
        for v_j in G.nodes:
            for b in range(t_max+1): # HACK! assumes integer edge length and start time of zero!
                reachable = set()
                for e in all_edges:
                    if (G.soonest_arrival(v_i, e.v_i) + e.length()
                        + G.soonest_arrival(e.v_j, v_j)) <= b:
                        reachable.update(e.samples())
                reachable_cache[(v_i, v_j, b)] = reachable

    store['reachable_cache'] = reachable_cache

def make_ma(run_dir):
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)
    P = store['P']
    G = store['G']
    waypoints = []
    waypoints.append((G.node_points[P[0].v_i][0], G.node_points[P[0].v_i][1]))
    for e in P:
        waypoints.append((G.node_points[e.v_j][0], G.node_points[e.v_j][1]))
    ppas.glider.make_ma(waypoints, os.path.join(run_dir, 'waypoints.ma'))

def calc_emse(run_dir):
    settings = pplan.PPlanSettings(run_dir)
    store = ppas.Store(settings.data_dir)
    P = store['P']
    G = store['G']
    objective = ppas.objectives.EMSEObjective(store['kmat'], settings.planner_properties['sigma_n'])
    start_t = ppas.datetime_to_seconds(settings.roi_properties['starttime'])
    samples = ppas.graph.path_samples(store['P'], start_t)
    print '%s: EMSE:' % run_dir, objective.f(samples)

def dummy(run_dir):
    time.sleep(10.)
    print run_dir

if __name__ == '__main__':
    cmd = PPlanCMD(num_processes=1)
    cmd.run()
