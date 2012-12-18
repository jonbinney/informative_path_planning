import numpy as np
import matplotlib
from matplotlib import pyplot as plt

class GraphPlotter:
    def __init__(self, G, variant='standard'):
        self.G = G
        self.variant = variant
        
    def plot(self, ax=None, t=0, nodenames=False, s=100, c='g', text_xoff=0.001, text_yoff=0.002):
        if ax == None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        if self.variant == 'xy':
            for v_i in self.G.nodes:
                sp_i = self.G.node_points[v_i]
                ax.scatter([sp_i[0]], [sp_i[1]], s=s, c='b')
                for v_j in self.G.neighbors(v_i):
                    sp_j = self.G.node_points[v_j]
                    ax.annotate('', sp_j, xytext=sp_i,
                                arrowprops=dict(linewidth=0, width=1,
                                                headwidth=4, frac=0.1, fc="b"))
                    if nodenames:
                        ax.annotate(str(v_i),
                                    xy=sp_i,
                                    xytext=(sp_i[0]+text_xoff, sp_i[1]+text_yoff),
                                    color=c)
            points = self.G.node_points
            xpad = (points[:,0].max() - points[:,0].min()) * 0.1
            ypad = (points[:,1].max() - points[:,1].min()) * 0.1
            ax.set_xlim((points[:,0].min()-xpad, points[:,0].max()+xpad))
            ax.set_ylim((points[:,1].min()-ypad, points[:,1].max()+ypad))
        else:
            dieeee_unknown_variant_
                
    def plot_path(self, P, ax=None, cmap=plt.cm.winter, text_offset=np.array((0.0, 0.0)),
        linewidth=8):
        if ax == None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        startp = self.G.node_points[P[0].v_i]
        endp = self.G.node_points[P[-1].v_j]
        #ax.annotate('s', xy=startp+text_offset, color='black')
        #ax.annotate('t', xy=endp+text_offset, color='black')

        path_vertices = []
        for e_i, e in enumerate(P):
            sp_i = self.G.node_points[e.v_i]
            sp_j = self.G.node_points[e.v_j]
            #ax.annotate('', sp_j, xytext=sp_i, arrowprops=dict(
            #    linewidth=1, width=4, headwidth=6, frac=0.2, fc=c))
            plt.plot([sp_i[0], sp_j[0]], [sp_i[1], sp_j[1]], linewidth=linewidth,
                color=cmap(float(e_i)/len(P)),
                solid_capstyle='round')
            path_vertices.append(sp_i)
        path_vertices.append(sp_j)
        path_vertices = np.array(path_vertices)
