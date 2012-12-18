'''
    Code for doing prediction with, and training of, Gaussian Processes

    Author: Jon Binney
    Date: 2009/5/20
'''
import numpy as np
from scipy import linalg, optimize
import kernels
import time

class GP:
    def __init__(self, X, Y, kernel, hyper_params):
        self.X = X
        self.Y = Y
        self.kernel = kernel
        self.hyper_params = hyper_params
    
    def train(self):
        '''
        Learn the hyper parameters by maximizing the marginal likelihood
        '''
        if len(self.X) == 0:
            'ERROR: Need points to learn hyperparameters', dieeeee
            
        self.training_log = []
        self.hyper_params = optimize.fmin(self.objective, self.hyper_params)
        
    def objective(self, hyper_params):
        '''
        Objective function to maximize when learning the hyper parameters
        during training.
        '''
        print 'hyper-params:', hyper_params
        X, Y = self.X, self.Y
        sigma_n = hyper_params[0]
        K = self.kernel.value(hyper_params[1:], X, X)
        L = np.matrix(linalg.cholesky(K + sigma_n**2 * np.eye(len(X)),
                                      lower = True))
        alpha = np.matrix(linalg.solve(L.T, linalg.solve(L, Y)))
        log_marginal = (-0.5*np.matrix(Y)*alpha.T - sum(np.log(np.diag(L))) -
                        len(X)/2.0*np.log(2*np.pi))
                        
        self.training_log.append( (hyper_params, -log_marginal.item()) )
        print 'log_marginal:', log_marginal

        print -log_marginal.item()
        
        return -log_marginal.item()
        
    def gradient(self, hyper_params):
    	'''
    	Gradient of likelihood function w.r.t. the hyper-parameters
    	
    	From Rasmussen pg 114, eq. 5.0
    	'''
    	g = np.zeros((len(hyper_params),))
    	X, Y = self.X, self.Y
    
    	# jacobian of K w.r.t. noise hyperparameter
    	sigma_n = hyper_params[0]
    	dk_dsn = 2.*sigma_n*np.matrix(np.eye(len(X)))
    	
    	# jacobian of K w.r.t. l
    	dk_dl = self.kernel.jacobian(hyper_params[1:], 0, X, X)
    	
    	K_f = self.kernel.value(hyper_params[1:], X, X)
    	K =  K_f +  sigma_n**2*np.matrix(np.eye(len(X)))
    	K_I = K.I
    	alpha = K_I*np.matrix(Y).T
    	g[0] = -0.5*np.trace((alpha*alpha.T - K_I)*dk_dsn)
    	g[1] = -0.5*np.trace((alpha*alpha.T - K_I)*dk_dl)
    	
    	print 'gradient:', g
    	
    	return g
    	
    def predict(self, X_p):
        '''
        Predict the values of the GP at each position x_p
        
        From Rasmussen & Williams "Gaussian Processes for Machine Learning",
        pg. 19, algorithm 2.1
        '''
        (X, Y) = (self.X, self.Y)
        sigma_n = self.hyper_params[0]
        K = self.kernel.value(self.hyper_params[1:], X, X)
        K_p = self.kernel.value(self.hyper_params[1:], X, X_p)
        K_p_p = self.kernel.value(self.hyper_params[1:], X_p, X_p)

        (self.K, self.K_p, self.K_p_p) = K, K_p, K_p_p

        # since the kernel is (should be) pos. def. and symmetric,
        # we can solve in a quick/stable way using the cholesky decomposition
        L = np.matrix(linalg.cholesky(K + sigma_n**2 * np.eye(len(X)),
                                      lower = True))
        alpha = np.matrix(linalg.solve(L.T, linalg.solve(L, Y)))
        f_p_mean = K_p.T * alpha.T
        v = np.matrix(linalg.solve(L, K_p))
        f_p_covariance = K_p_p - v.T*v
        log_marginal = (-0.5*np.matrix(Y)*alpha.T - sum(np.log(np.diag(L))) -
                        len(X)/2.0*np.log(2*np.pi))

        return (np.array(f_p_mean).flatten(),
                f_p_covariance,
                np.array(log_marginal).flatten())


def predict(kernel, Xi, Y, Xi_p):
    '''
    Predict the values of the GP at each position x_p
    
    From Rasmussen & Williams "Gaussian Processes for Machine Learning",
    pg. 19, algorithm 2.1
    '''
    K = kernel.value(Xi, Xi)
    K_p = kernel.value(Xi, Xi_p)
    K_p_p = kernel.value(Xi_p, Xi_p)

    # since the kernel is (should be) pos. def. and symmetric,
    # we can solve in a quick/stable way using the cholesky decomposition
    L = np.matrix(linalg.cholesky(K + sigma_n**2 * np.eye(len(Xi)),
                                  lower = True))
    alpha = np.matrix(linalg.solve(L.T, linalg.solve(L, Y)))
    f_p_mean = K_p.T * alpha.T
    v = np.matrix(linalg.solve(L, K_p))
    f_p_covariance = K_p_p - v.T*v
    log_marginal = (-0.5*np.matrix(Y)*alpha.T - sum(np.log(np.diag(L))) -
                    len(Xi)/2.0*np.log(2*np.pi))

    return (np.array(f_p_mean).flatten(),
            f_p_covariance,
            np.array(log_marginal).flatten())    
    
