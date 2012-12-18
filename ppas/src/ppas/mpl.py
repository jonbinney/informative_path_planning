from matplotlib import pyplot as plt
import matplotlib as mpl

def latex_matplotlib_setup():
    '''
    Changes matplotlib settings so that it will produce plots
    that look good in latex documents.
    '''
    params = {'backend': 'gtk',
              'axes.labelsize': 10,
              'text.fontsize': 10,
              'legend.fontsize': 8,
              'xtick.labelsize': 10,
              'ytick.labelsize': 10,
              'text.usetex': True,
              'font.family':'serif',
              'font.serif':'times'
              }
    plt.rcParams.update(params)

def make_fig_and_axes(fig_shape=None, axes_box=[0.2, 0.2, 0.7, 0.7]):
    '''
    fig_shape - (figure width in cm, figure_height in cm)
    '''
    if fig_shape == None:
        fig = plt.figure()
    else:
        fig = plt.figure(figsize=(fig_shape[0]/2.54, fig_shape[1]/2.54))
    ax = fig.add_axes(axes_box)
    return fig, ax

