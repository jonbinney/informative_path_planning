import numpy as np
from scipy import linalg

class CEObjective:
    '''
    Objective: REDUCTION in conditional entropy
    '''
    def __init__(self, Kmat, sigma_n, Xi_pilot, Xi_test):
        self.kernel = kernel
        self.sigma_n = sigma_n
        self.Xi_all = Xi_all

    def f(self, Xi):
        Xi_path = self.expander.h(P, start_t)
        Xi_sofar = set.union(Xi_path, self.Xi_pilot)
        Xi_test = self.Xi_all.difference(Xi_sofar)
        mi =  gaussian.mutual_information(
            self.kernel, self.sigma_n,
            self.Xi_pilot,
            Xi_path,
            Xi_test)
        return mi

class ContinuousEMSE:
    def __init__(self, kernel, hyper_params, X_test, sigma_n, X_pilot=None):
        self.kernel = kernel
        self.hyper_params = hyper_params
        self.X_test = X_test
        self.sigma_n = sigma_n
        self.X_pilot = X_pilot
        self.K_pp = self.kernel.value(self.hyper_params, self.X_test, self.X_test)

    def f(self, X_samples):
        return -np.mean(np.diag(self.calc_posterior_cov(X_samples)))
    
    def calc_posterior_cov(self, X_samples):
        #X_samples = np.vstack((self.X_pilot, X_samples))
        
        K = self.kernel.value(self.hyper_params, X_samples, X_samples)
        K_p = self.kernel.value(self.hyper_params, X_samples, self.X_test)

        # since the kernel is (should be) pos. def. and symmetric,
        # we can solve in a quick/stable way using the cholesky decomposition
        L = np.matrix(
            linalg.cholesky(
                K + self.sigma_n**2 * np.eye(len(X_samples)),
                lower = True))

        v = np.matrix(linalg.solve(L, K_p))
        return self.K_pp - v.T*v


class EMSEObjective:
    '''
    Objective: REDUCTION in expected mean square error
    '''
    def __init__(self, Kmat, sigma_n, conditioned_on=set()):
        self.Kmat = Kmat
        self.sigma_n = sigma_n
        self.conditioned_on = conditioned_on
        self.value = None
        self.num_evaluations = 0

    def f(self, Xi, update_dist=False):
        '''
        Condition on the points Xi, and return the new -EMSE

        If update_dist is True, this method permanently alters
        the covariance matrix of the class
        '''
        self.num_evaluations += 1
        Xi = Xi.difference(self.conditioned_on)

        if len(Xi) == 0:
            # we're not conditioning on any points
            self.value = -np.mean(np.diag(self.Kmat))
            return self.value

        Xi_list = list(Xi)
        K = self.Kmat[Xi_list,:][:,Xi_list]
        K_p = self.Kmat[Xi_list,:]

        # since the kernel is (should be) pos. def. and symmetric,
        # we can solve in a quick/stable way using the cholesky decomposition
        L = np.matrix(
            linalg.cholesky(
                K + self.sigma_n**2 * np.eye(len(Xi)),
                lower = True))

        v = np.matrix(linalg.solve(L, K_p))
        kmat_new = self.Kmat - v.T*v

        # update the objective function value
        value_new = -np.mean(np.diag(kmat_new))

        # update our distribution
        if update_dist:
            self.Kmat = kmat_new
            self.conditioned_on.update(Xi)
        self.value = value_new

        if self.value > 0:
            dieeeee
        
        return value_new

    def copy(self):
        newcopy = EMSEObjective(
            self.Kmat.copy(), self.sigma_n, self.conditioned_on.copy())
        return newcopy
