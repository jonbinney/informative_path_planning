#!/usr/bin/env python
import roslib; roslib.load_manifest('pplan')
import os, os.path
import numpy as np
from matplotlib import pyplot as plt
import ppas

run_dir = os.getcwd()
data_dir = os.path.join(run_dir, 'data')
s = ppas.Store(data_dir)


