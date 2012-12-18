import sys, shelve, os

# set the directory for the run (where data files will written to/read from)
run_dir = sys.argv[1]
print 'run_dir is', run_dir

# read variables in from the settings file for this run
execfile(os.path.join(run_dir, 'settings.py'))

# save everything to a python shelf
s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
G = s['G']
points = s['points']
Xi_pilot = s['Xi_pilot']
s.close()
