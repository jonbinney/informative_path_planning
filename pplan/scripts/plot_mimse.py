import sys, time, shelve, os.path
import numpy as np
from scipy import linalg
from scipy import stats
import matplotlib
from matplotlib import rc
rc('font',**{'family':'serif','serif':['Times']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)
from matplotlib import pyplot as plt
import gp, jgraph

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# load variables from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# load the graph, points, and precomputed kernel values from file
s = shelve.open(os.path.join(run_dir, 'pathdata.dat'))
trials = s['trials']
s.close()

colors = 'bgrcmykw'
formats = ['-', '--', '-.', ':']

# plot mi
trialnum = 0
diffs = []
ratios = []
for trial in trials:
    trialnum += 1
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_xlabel('Path Length', fontsize=20)
    ax.set_ylabel('Mutual Information', fontsize=20)
    results = trial['results']
    path_lens = [len(P) for P in results['rgh']['path_list']]
    rgh_mi_arr = np.array(results['rgh']['mi_list'])
    greedy_mi_arr = np.array(results['greedy']['mi_list'])
    diffs.append(rgh_mi_arr - greedy_mi_arr)
    ratios.append(rgh_mi_arr / greedy_mi_arr)
    ax.plot(path_lens, rgh_mi_arr, 'b-')
    ax.plot(path_lens, greedy_mi_arr, 'b--')
    fig.savefig(os.path.join(run_dir, 'miplot%d.pdf' % trialnum))

# plot mse
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
rgh_data = {}
greedy_data = {}
mse_diffs = []
for trial in trials:
    results = trial['results']
    rgh_mse = np.array(results['rgh']['mse_list'])
    greedy_mse = np.array(results['greedy']['mse_list'])
    mse_diffs.append(rgh_mse - greedy_mse)
    path_lens = [len(P) for P in results['rgh']['path_list']]

plt.errorbar(path_lens, np.mean(mse_diffs, axis=0),
             yerr=np.std(mse_diffs, axis=0), fmt='-')
ax.set_title('MSE of RGH - MSE of Greedy vs. Path Length')
ax.set_xlabel('Path Length')
ax.set_ylabel('Mean Squared Error')

fig.savefig(os.path.join(run_dir, 'mseplot.pdf'))

#plt.show()
