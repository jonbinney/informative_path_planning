import roslib; roslib.load_manifest('pplan')
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111)
lines = ax.plot(np.sin(np.linspace(0, 12, 1000)))
lines[0].set_picker(10)
pickevent = None

def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        event.button, event.x, event.y, event.xdata, event.ydata)

def onpick(event):
    thisline = event.artist
    xdata, ydata = thisline.get_data()
    ind = event.ind
    print dir(event)
    print dir(event.artist)
    x, y = xdata[ind], ydata[ind]
    print 'on pick line:', x, y
    event.artist.axes.plot(x[:1], y[:1], 'ro')
    plt.draw()

    

#cid = fig.canvas.mpl_connect('button_press_event', onclick)
cid = fig.canvas.mpl_connect('pick_event', onpick)
plt.show()
