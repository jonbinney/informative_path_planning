#!/usr/bin/env python
import roslib
roslib.load_manifest('pplan')
import sys, time, os, os.path, multiprocessing, datetime, signal
import numpy as np

import pplan, ppas

run_dir = sys.argv[1]

print '%s: getting data' % run_dir
settings = pplan.PPlanSettings(run_dir)
store = ppas.Store(settings.data_dir)

