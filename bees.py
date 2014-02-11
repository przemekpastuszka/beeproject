from itertools import chain
from world_objects import Flower, Hive, Obstacle, Grass


class Bee(object):
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.position = (0, 0)
        self.pollen_gathered = 0

    def choose_action(self, meadow, directions):
        raise NotImplemented

    def interact_with(self, meadow_object):
        """
           When meadow object is of type Bee can interact with,
           performs an interaction
        """
        if isinstance(meadow_object, Flower):
            pollen_to_gather = min(self.max_capacity - self.pollen_gathered,
                                   meadow_object.pollen)
            meadow_object.pollen -= pollen_to_gather
            self.pollen_gathered += pollen_to_gather

        if isinstance(meadow_object, Hive):
            meadow_object.pollen += self.pollen_gathered
            self.pollen_gathered = 0

    def __str__(self):
        return 'B'


class RandomFlightBee(Bee):
    def choose_action(self, meadow, directions):
        return choice(directions)


class NeuralBee(Bee):
    """
       Bee acting under control of neural network
    """
    visibility_radius = 1

    def __init__(self, max_capacity, network):
        Bee.__init__(self, max_capacity)
        self.network = network

    def choose_action(self, meadow, directions):
        """
           Asks neural network for next move
        """
        visible_objects = []
        for row_shift in range(-self.visibility_radius,
                               self.visibility_radius + 1):
            for column_shift in range(-self.visibility_radius,
                                      self.visibility_radius + 1):
                x = self.position[0] + row_shift
                y = self.position[1] + column_shift

                visible_objects.append(meadow.meadow_objects[x][y])

        input_params = list(chain.from_iterable(
            map(NeuralBee._encode_meadow_object, visible_objects))
        )
        input_params.append(self.pollen_gathered / float(self.max_capacity))
        output = self.network.activate(input_params)
        maximum_output_index = list(output).index(max(output))

        return directions[maximum_output_index]

    @staticmethod
    def _encode_meadow_object(meadow_object):
        """
           Returns representation of meadow object in format understandable by
           neural network, independent from representation used to display
           final results
        """
        encoding = {Grass: [0, 0, 0],
                    Hive: [1, 0, 0],
                    Flower: [0, 1, 0],
                    Obstacle: [0, 0, 1]}
        return encoding[type(meadow_object)]
