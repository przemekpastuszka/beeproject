from itertools import chain
from utils import sgn
import random
from world_objects import Flower, Hive, Obstacle, Grass


class Bee(object):
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.position = (0, 0)
        self.pollen_gathered = 0

    def choose_action(self, meadow, directions, all_bees):
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
    visibility_radius = 2

    def __init__(self, max_capacity, network, hive_positions):
        Bee.__init__(self, max_capacity)
        self.network = network
        self.hive_position = hive_positions[0]

    def choose_action(self, meadow, directions, all_bees):
        return self._choose_determinant_action(meadow, directions, all_bees) if random.random() < 0.8 else random.choice(directions)
        
    def _choose_determinant_action(self, meadow, directions, all_bees):
        if self.pollen_gathered >= self.max_capacity:
            return (sgn(self.hive_position[0] - self.position[0]),
                    sgn(self.hive_position[1] - self.position[1]))
        else:
            return self._neural_move(meadow, directions, all_bees)
        
    def _neural_move(self, meadow, directions, all_bees):
        """
           Asks neural network for next move
        """
        visible_objects = []
        for row_shift in xrange(-self.visibility_radius,
                               self.visibility_radius + 1):
            for column_shift in xrange(-self.visibility_radius,
                                      self.visibility_radius + 1):
                if not row_shift and not column_shift:
                    continue
                
                x = self.position[0] + row_shift
                y = self.position[1] + column_shift
                
                bee = self._find_bee_for_coords(all_bees, x, y)
                if bee is None:
                    visible_objects.append(meadow.meadow_objects[x][y])
                else:
                    visible_objects.append(bee)

        input_params = map(NeuralBee._encode_meadow_object, visible_objects)
        output = self.network.activate(input_params)
        maximum_output_index = output.index(max(output))

        return directions[maximum_output_index]

    def _find_bee_for_coords(self, bees, x, y):
        for bee in bees:
            if bee.position == (x, y):
                return bee
        return None

    @staticmethod
    def _encode_meadow_object(meadow_object):
        """
           Returns representation of meadow object in format understandable by
           neural network, independent from representation used to display
           final results
        """
        meadow_object_type = type(meadow_object)
        if (isinstance(meadow_object, Flower) and meadow_object.pollen == 0) or isinstance(meadow_object, Hive):
            meadow_object_type = Grass
        
        encoding = {Grass: 0,
                    NeuralBee: -2,
                    Flower: 1,
                    Obstacle: -1}
        return encoding[meadow_object_type]
