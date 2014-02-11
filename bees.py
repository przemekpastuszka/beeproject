from itertools import chain
from utils import sgn
import random
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


class NeuralBee(Bee):
    """
       Bee acting under control of neural network
    """
    visibility_radius = 1

    def __init__(self, max_capacity, network, hive_positions):
        Bee.__init__(self, max_capacity)
        self.network = network
        self.hive_position = hive_positions[0]

    def choose_action(self, meadow, directions):
        return self._choose_determinant_action(meadow, directions) if random.random() < 0.7 else random.choice(directions)
        
    def _choose_determinant_action(self, meadow, directions):
        if self.pollen_gathered >= self.max_capacity:
            return (sgn(self.hive_position[0] - self.position[0]), sgn(self.hive_position[1] - self.position[1]))
        else:
            return self._neural_move(meadow, directions)
        
    def _neural_move(self, meadow, directions):
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
        meadow_object_type = type(meadow_object)
        
        if isinstance(meadow_object, Flower) and meadow_object.pollen == 0:
            meadow_object_type = Grass
        
        encoding = {Grass: [0, 0, 0],
                    Hive: [1, 0, 0],
                    Flower: [0, 1, 0],
                    Obstacle: [0, 0, 1]}
        return encoding[meadow_object_type]
