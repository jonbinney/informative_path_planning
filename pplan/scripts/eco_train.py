import roslib; roslib.load_manifest('pplan')
import os.path
import numpy as np
import pplan, ppas

run_dir = '/home/jdb/Research/papers/2011_icra/runs/pudding1/'
s = ppas.Store(os.path.join(run_dir, 'data'))
data = s['training_data'][::16]

# lat, lon
X = data[:,1:3]

# temperature (de-meaned)
Y = data[:,4]
Y -= Y.mean()

print 'Creating GP'
initial_hyper_params =  np.array([1.0, 1.0, 0.1])
kernel = ppas.gp.kernels.RBF()
gp = ppas.gp.GP(X, Y, kernel, initial_hyper_params)

print 'Training GP with %d data points' % len(X)
gp.train()

print 'Trained hyper params:', gp.hyper_params
