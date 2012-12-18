# construct the Gaussian Process
kernel = ppas.gp.kernels.WeightedExponential()
if mode in ['vanilla', 'edge']:
    # 2D input data, both dimensions spatial
    hyper_params = np.array((0.025, 0.05, 0.1, 0.1))

    # precompute all the kernel values
    Kmat = kernel.value(hyper_params[1:], points, points)
elif mode in ['time', 'edgetime']:
    # 3D input data, first two are spatial and third is time
    hyper_params = np.array((5.216e-4, .014, .108, .196, .619))

    # precompute all the kernel values
    Kmat = kernel.value(hyper_params[1:], points, points)
elif mode in ['depth_transect']:
    # sigma_n, sigma_f, lat, lon, depth, time
    #hyper_params = np.array((5.216e-4, .014, .001, .001, .01, 0.0))
    hyper_params = np.array((0.1, 1.0, 10.0, 10.0, 0.02, 0.0))

    # precompute all the kernel values
    Kmat = kernel.value(hyper_params[1:], points, points)
else:
    _bad_mode_setting_

X_pilot = []
if train_gp:
    # use ML training to find the hyper-parameters
    test_gp = ppas.gp.GP(X_pilot, Y_pilot, kernel, hyper_params)
    test_gp.train()
    hyper_params = test_gp.hyper_params

