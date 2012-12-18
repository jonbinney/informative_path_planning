import time

verbose = True
starttime = time.time()

def init():
    global starttime
    starttime = time.time()
    
def printdbg(msg_str, always=False):
    if verbose or always:
        print '%0.4f:' % (time.time()-starttime,), msg_str
