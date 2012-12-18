'''
    kernels.py - kernels (covariance matrices) for use with my GP code. Each
    kernel class should implement two member functions:

    value(self, hyper_params, X1, X2)
      Creates and returns the kernel matrix for the two inputs, using the
      given hyper parameters. Kernel must be positive definite.

    jacobian(self, hyper_params, hp_i, X1, X2)
      Creates and returns the jacobian of th kernel  matrix for the two inputs,
      using the given hyper parameters, evalutated for hyper parameter hp_i

    Author: Jon Binney
    Date: 2009/5/20
'''

import numpy as np
import time
from scipy import linalg

class WeightedRBF:
    def __init__(self):
        pass

    def value(self, hyper_params, X1, X2):
        sigma_f = hyper_params[0]
        W = np.matrix(np.diag(hyper_params[1:]**2))
        K = np.matrix(np.zeros((len(X1), len(X2))))
        for ii in range(len(X1)):
            for jj in range(len(X2)):
                x1 = np.matrix(X1[ii]).T
                x2 = np.matrix(X2[jj]).T
                K[ii,jj] = sigma_f**2 * np.exp(-0.5*(x1-x2).T*W*(x1-x2))
        return K

class RBF:
    def __init__(self):
        pass

    def value(self, hyper_params, X1, X2):
        sigma_f = hyper_params[0]
        w = hyper_params[1]**2
        squared_dist = np.zeros((len(X1), len(X2)))
        for d in range(X1.shape[1]):
            M1 = np.tile(X1[:,d:d+1], (1, len(X2)))
            M2 = np.tile(np.transpose(X2[:,d:d+1]), (len(X1), 1))
            squared_dist += (M1 - M2)**2
        return sigma_f**2 * np.exp(-0.5 * w * squared_dist)

    def value_py(self, hyper_params, X1, X2):
        # print time.time(), 'allocating kernel matrix'
        sigma_f = hyper_params[0]
        W = hyper_params[1]**2 # not a matrix, just a scalar
        K = np.matrix(np.zeros((len(X1), len(X2))))
        for ii in range(len(X1)):
            for jj in range(len(X2)):
                x1 = np.matrix(X1[ii]).T
                x2 = np.matrix(X2[jj]).T
                K[ii,jj] = sigma_f**2 * np.exp(-0.5*(x1-x2).T*W*(x1-x2))
        return K

class PreComputed:
    def __init__(self, Kmat):
        self.Kmat = Kmat

    def value(self, Xi, Xj):
        # print time.time(), 'allocating kernel matrix'
        K = self.Kmat[Xi,:][:,Xj]
	   
        return K


class Noise:
    def __init__(self):
        pass

    def value(self, hyper_params, X):
        sigma_n = hyper_params[0]
        print time.time(), 'creating noise matrix'        
        return np.matrix(sigma_n * eye(len(X)))

    def jacobian(self, hyper_params, hp_i, X):
        pass
