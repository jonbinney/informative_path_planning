'''
Run this using "run -i". Expects run_dir to be set.
'''
import sys, os.path, shelve
import roslib
roslib.load_manifest('pplan')

import ppas

# read variables in from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

shelf_path = os.path.join(run_dir, 'data.shelf')
print 'Loading variables from %s:' % shelf_path
s = shelve.open(shelf_path)
g = globals()
for k in s.keys():
    print '   ', k
    g[k] = s[k]
s.close()
