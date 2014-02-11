from collections import namedtuple


Directions = namedtuple('Directions', ['left', 'right', 'up', 'down'])


class Board(namedtuple('Board', ['width', 'height'])):

    @property
    def size(self):
        return reduce(lambda x, y: x * y, self)

    def remaining_space(self, objects_distribution):
        return self.size - objects_distribution.count


class ObjectsDistribution(namedtuple('ObjectDistribution',
                                     ['obstacles', 'flowers', 'hives'])):

    @property
    def count(self):
        return sum(self)


NetworkParams = namedtuple('NetworkParams',
                           ['inputs', 'hidden_neurons', 'outputs'])

def sgn(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0