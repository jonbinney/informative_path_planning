import roslib
roslib.load_manifest('pplan')
import time
import numpy as np
from scipy import linalg
from matplotlib import pyplot as plt

def make_cov_matrix(n, dtype):
    return np.eye(n, dtype=dtype) + 0.1*np.ones((n, n), dtype=dtype)

n_list = range(100, 4000, 500)

time_list_32bit = []
for n in n_list:
    m = make_cov_matrix(n, np.float32)
    t0 = time.time()
    linalg.cholesky(m)
    t1 = time.time()
    time_list_32bit.append(t1-t0)

time_list_64bit = []
time_list_64bit_copies = []
for n in n_list:
    m = make_cov_matrix(n, np.float)
    
    t0 = time.time()
    mprime = m.copy()
    t1 = time.time()
    time_list_64bit_copies.append(t1-t0)
    
    t0 = time.time()
    linalg.cholesky(m)
    t1 = time.time()
    time_list_64bit.append(t1-t0)

plt.plot(n_list, time_list_32bit, 'r')
plt.plot(n_list, time_list_64bit, 'b')
plt.plot(n_list, time_list_64bit_copies, 'g')
plt.show()
