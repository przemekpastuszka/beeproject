from itertools import chain
from utils import sgn
import random
from world_objects import Flower, Hive, Obstacle, Grass


class Bee(object):
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.position = (0, 0)
        self.pollen_gathered = 0.0

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
    state = 1

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

        input_params = list(chain.from_iterable((map(NeuralBee._encode_meadow_object, visible_objects))))
        input_params.append(self.pollen_gathered / self.max_capacity)
        
        output = self.network.activate(input_params)
        
        self.state = output[4]
        
        directions_indicators = output[:4]
        direction_index = directions_indicators.index(max(directions_indicators))

        return directions[direction_index]

    def _find_bee_for_coords(self, bees, x, y):
        for bee in bees:
            if bee.position == (x, y):
                return bee
        return None
    
    @staticmethod
    def network_input_size():
        return ((NeuralBee.visibility_radius * 2 + 1) ** 2 - 1) * len(NeuralBee._encode_meadow_object(Grass())) + 1
    
    @staticmethod
    def _encode_meadow_object(meadow_object):
        """
           Returns representation of meadow object in format understandable by
           neural network, independent from representation used to display
           final results
        """
        
        encoders = {Grass: lambda x: [0, 0, 0],
                    Hive: lambda x: [0, 0, 0],
                    NeuralBee: lambda x: [x.state, 0, 0],
                    Flower: lambda x: [0, 0, 0] if x.pollen == 0 else [0, 1, 0],
                    Obstacle: lambda x: [0, 0, 1]}
        return encoders[type(meadow_object)](meadow_object)