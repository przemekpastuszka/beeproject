from utils import Directions, Board, ObjectsDistribution, NetworkParams

DIRECTIONS = Directions(left=(-1, 0),
                        right=(1, 0),
                        up=(0, 1),
                        down=(0, -1))

BOARD = Board(width=10, height=10)

OBJECTS_DISTRIBUTION = ObjectsDistribution(obstacles=10,
                                           flowers=10,
                                           hives=1)

NETWORK_PARAMS = NetworkParams(inputs=24,
                               hidden_neurons=9,
                               outputs=5)

BEES_NUMBER = 3

NETWORK_EVALUATIONS = 5

EPISODES_PER_SIMULATION = 300

BEE_MAX_CAPACITY = 5.0

FLOWER_CAPACITY = 10.0
