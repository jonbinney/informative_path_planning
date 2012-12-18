import roslib; roslib.load_manifest('pplan')
import sys, os.path
import numpy as np
from matplotlib import pyplot as plt
import ppas, pplan

# load settings
run_dir = sys.argv[1]
result_num = sys.argv[2]
settings = pplan.PPlanSettings(run_dir)
store = ppas.Store(settings.data_dir)

# setup plot
fig = plt.figure()
ax = fig.add_subplot(111)

G = store['G']
if not 'bonelli' in run_dir:
    G.node_points = G.node_points[:,::-1]
graph_plotter = ppas.plot.GraphPlotter(G, 'xy')
graph_plotter.plot(ax=plt.gca(), nodenames=True, text_xoff=0.00005, text_yoff=0.00005)

results = store[os.path.join('results/%s/result' % result_num)]
graph_plotter.plot_path(results['P'], ax)

plt.show()
