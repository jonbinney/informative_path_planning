'''
Run this using "run -i". Expects run_dir to be set.
'''
import sys, os.path, shelve

shelf_path = os.path.join(run_dir, 'data.shelf')
print 'Saving variables to %s:' % shelf_path
s = shelve.open(shelf_path)
g = globals()
for k in sys.argv[1:]:
    print '   ', k
    s[k] = g[k]
s.close()
