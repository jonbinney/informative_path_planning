import os, sys
import matplotlib.pyplot as plt
files = []
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111)
for i in range(50): # 50 frames
ax.cla()
ax.imshow(rand(5,5), interpolation=’nearest’)
fname = ’_tmp%03d.png’%i
print ’Saving frame’, fname
fig.savefig(fname)
files.append(fname)
print ’Making movie animation.mpg - this make take a while’
os.system("mencoder ’mf://_tmp*.png’ -mf type=png:fps=10 \\
-ovc lavc -lavcopts vcodec=wmv2 -oac copy -o animation.mpg")

