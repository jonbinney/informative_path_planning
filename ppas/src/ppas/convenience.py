import sys, shelve, os
import ppas

def load_var(run_dir, varname):
    # save everything to a python shelf
    s = shelve.open(os.path.join(run_dir, 'graphdata.dat'))
    var = s[varname]
    s.close()

    return var
