import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from scipy import linalg, stats
import ppas.graph

class SphereObstacle:
    def __init__(self, x_c, r):
        self.x_c = x_c
        self.r = r

    def collides(self, x):
        if linalg.norm(x - self.x_c) <= self.r:
            return True
        else:
            return False

def state_is_free(x, obstacles):
    for ob in obstacles:
        if ob.collides(x):
            return False
    return True
    
def random_state(x_min, x_max, x_start, x_goal):
    if stats.uniform.rvs() > 0.5:
        return x_goal
    else:
        D = len(x_min)
        x_rand = np.zeros(D)
        for d_i in range(D):
            x_rand[d_i] = stats.uniform.rvs(x_min[d_i], x_max[d_i]-x_min[d_i])
        return x_rand

def nearest_neighbor(x_rand, T):
    v_nearest = None
    d_min = np.inf
    for v in T.nodes:
        d = linalg.norm(v.x - x_rand)
        if d < d_min:
            v_nearest = v
            d_min = d
    return v_nearest

def select_input(x_rand, x_near, model_params):
    vel = model_params['vel']
    direction = (x_rand - x_near) / linalg.norm(x_rand - x_near)
    u = direction * vel
    return u

def new_state(x, u, t_delta, model_params, obstacles):
    x_new = x + u*t_delta
    if state_is_free(x_new, obstacles):
        return x_new
    else:
        return None

if __name__ == '__main__':
    model_params = {'vel':1.0}
    t_delta = .01
    x_start = np.array((0.0, 0.0))
    x_goal = np.array((1.0, 1.0))
    ob1 = SphereObstacle(np.array((0.25, 0.25)), 0.2)
    obstacles = [ob1]

    # initialize the tree with the start node
    v_start = ppas.graph.Node(x=x_start)
    T = ppas.graph.Graph(set([v_start]))

    x_min = np.array([-1.0, -1.0])
    x_max = np.array([1.0, 1.0])
    rand_points = []
    for ii in range(500):
        # choose a point randomly from the state space
        x_rand = random_state(x_min, x_max, x_start, x_goal)
        rand_points.append(x_rand)

        # find the nearest node already in the tree
        v_near = nearest_neighbor(x_rand, T)
        x_near = v_near.x

        # choose the input that moves the robot towards the
        # randomly selected state
        u = select_input(x_rand, x_near, model_params)

        # add the new state to the tree
        x_new = new_state(x_near, u, t_delta, model_params, obstacles)
        if x_new != None:
            v_new = ppas.graph.Node(x=x_new)
            T.add_node(v_new)
            e = ppas.graph.Edge(v_near, v_new, linalg.norm(x_new-x_near))
            T.add_edge(e)

    # plot the tree
    gp = ppas.plot.GraphPlotter(T)
    gp.plot(s=10)    
    ax = plt.gca()    
    for ob in obstacles:
        ax.add_patch(Circle(ob.x_c, ob.r, color='y'))
    plt.plot([v_start.x[0]], [v_start.x[1]], 'ro')
    plt.plot([x[0] for x in rand_points],
             [x[1] for x in rand_points], 'g.')
    plt.show()    
        
                
        
