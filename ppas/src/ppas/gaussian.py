import numpy as np
from scipy import linalg

def covariance(kernel, sigma_n, Xi, Xi_p):
    K = kernel.value(Xi, Xi)
    K_p = kernel.value(Xi, Xi_p)
    K_p_p = kernel.value(Xi_p, Xi_p)

    if K.shape == (0, 0):
        # we're not conditioning on any points. just return the covariance
        return K_p_p
    
    # since the kernel is (should be) pos. def. and symmetric,
    # we can solve in a quick/stable way using the cholesky decomposition
    L = np.matrix(
        linalg.cholesky(
            K + sigma_n**2 * np.eye(len(Xi)),
            lower = True))

    v = np.matrix(linalg.solve(L, K_p))
    f_p_covariance = K_p_p - v.T*v

    #if np.sum(linalg.eigvals(f_p_covariance) > 0.0) < len(f_p_covariance):
    #    dieeeeee  # covariance not full rank
        
    return f_p_covariance

def correlation(K):
    # construct the correlation matrix from the covariance matrix
    K = np.array(K)
    C = np.zeros((len(K), len(K)))
    for ii in range(len(K)):
        for jj in range(len(K)):
            C[ii][jj] = K[ii][jj] / (K[ii][ii]**0.5 * K[jj][jj]**0.5)
    return C

def entropy(K):
    '''
    Calculate the entropy of a multivariate Gaussian distribution,
    using a cholesky/log trick to deal with covariance matrices whose
    determinants are too small/large to fit in a double precision float,
    but whose log determinant is not.

    Args:
    K - covariance matrix of the gaussian
    '''

    # we know that the matrix is symmetric and positive definite,
    # because it is a covariance matrix, so we use cholesky
    # decomposition to get a lower triangular matrix
    L = linalg.cholesky(K)

    # determinant of a lower triangular matrix is prod(diag(K)), so
    # log(det(K)) = log(prod(diag(K))) = sum(log(diag(K)))
    logdet = np.sum(np.log(np.diag(L)))*2.0
    entropy = 0.5*(len(K)*np.log(2*np.pi*np.e) + logdet)

    return np.real(entropy)

def mutual_information(kernel, sigma_n, Xi_pilot, Xi_path, Xi_test):
    '''
    Calculates mutual information of variables Xi_test w.r.t. Xi_path,
    assuming that the variables Xi_pilot are known, and that all
    variables are modeled as a Gaussian process with the given kernel
    and noise variance.

    kernel - kernel object for the gaussian process
    sigma_n - noise variance for the gaussian process
    Xi_pilot - (set) of pilot samples
    Xi_path - (set) of path samples
    Xi_test - (set) of test samples
    '''

    # putting the sample sets into array form lets us pass them into
    # C easily, where we can efficiently build the kernel matrix
    Xi_pilot = np.array(list(Xi_pilot), dtype=np.int)
    Xi_path = np.array(list(Xi_path), dtype=np.int)
    Xi_test = np.array(list(Xi_test), dtype=np.int)
    
    cov_without = covariance(kernel, sigma_n, Xi_pilot, Xi_test)
    cov_with = covariance(kernel, sigma_n, 
     	np.concatenate([Xi_pilot, Xi_path]), Xi_test)
    entropy_without = entropy(cov_without)
    entropy_with = entropy(cov_with)
    mi = entropy_without - entropy_with

    # if mutual information is NaN, then something went wrong. most likely
    # the covariance matrix has become singular. bad things are happening.
    if np.isnan(mi):
        diiiiiieeeeeee
        
    return mi

def expected_mse(kernel, sigma_n, Xi_samples, Xi_test):
    '''
    Calculates expected mean square error of variables Xi_test w.r.t. Xi_path,
    assuming that the variables Xi_pilot are known, and that all
    variables are modeled as a multivariate gaussian with the given kernel
    and noise variance.

    kernel - kernel object for the gaussian process
    sigma_n - noise variance for the gaussian process
    Xi_pilot - (set) of pilot samples
    Xi_path - (set) of path samples
    Xi_test - (set) of test samples
    '''
    cov = covariance(kernel, sigma_n, Xi_samples, Xi_test)
    emse = np.mean(np.diag(cov))
    
    # if mutual information is NaN, then something went wrong. most likely
    # the covariance matrix has become singular. bad things are happening.
    if np.isnan(emse):
        diiiiiieeeeeee
        
    return emse
