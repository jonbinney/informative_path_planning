class PointSet:
    '''
    Stores a set of points, with an index for each. A mapping is
    maintained both from index to point, and point to index, in order
    to allow for fast lookups.
    '''
    def __init__(self):
        self.n = 0
        self.p_to_i = {}
        self.i_to_p = {}

    def add(self, point):
        point = tuple(point)
        if point in self.p_to_i:
            return self.p_to_i[point]
        else:
            new_i = self.n
            self.n += 1
            self.i_to_p[new_i] = point
            self.p_to_i[point] = new_i
            return new_i

    def get_index(self, point):
        return self.p_to_i[tuple(point)]

    def get_point(self, index):
        return self.i_to_p[int(index)]

    def get_points(self, indices):
        return [self.get_point(i) for i in indices]

    def get_indices(self, points):
        return [self.get_index(p) for p in points]

    def get_all_points(self):
        return self.get_points(range(self.n))

    def get_all_indices(self):
        return range(self.n)

