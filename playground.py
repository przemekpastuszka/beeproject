'''
Created on Dec 7, 2013

@author: przemek
'''
from random import choice, shuffle
from time import sleep
from itertools import chain
from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.environments.fitnessevaluator import FitnessEvaluator
from pybrain.optimization.hillclimber import HillClimber
from pybrain.optimization import FEM, ExactNES, GA

class Action(object):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, 1)
    DOWN = (0, -1)

class WorldObject(object):
    def reset_state(self):
        pass

class Flower(WorldObject):
    def __init__(self, initial_capacity):
        self.initial_capacity = initial_capacity
        self.reset_state()
    
    def reset_state(self):
        self.pollen = self.initial_capacity
    
    def __str__(self):
        return 'F' if self.pollen > 0 else 'X' 

class Hive(WorldObject):
    def __init__(self):
        self.reset_state()
    
    def reset_state(self):
        self.pollen = 0
        
    def __str__(self):
        return 'H'

class Obstacle(WorldObject):
    def __str__(self):
        return 'O'

class Grass(WorldObject):
    def __str__(self):
        return '.'

class Bee(WorldObject):
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.initial_position = (0, 0)
        self.reset_state()
    
    def choose_action(self, meadow):
        pass
    
    def interact_with(self, meadow_object):
        if issubclass(type(meadow_object), Flower):
            pollen_to_gather = min(self.max_capacity - self.pollen_gathered, meadow_object.pollen)
            meadow_object.pollen -= pollen_to_gather
            self.pollen_gathered += pollen_to_gather
            
        if issubclass(type(meadow_object), Hive):
            meadow_object.pollen += self.pollen_gathered
            self.pollen_gathered = 0
    
    def reset_state(self):
        self.position = self.initial_position
        self.pollen_gathered = 0
            
    def __str__(self):
        return 'B'

class RandomFlightBee(Bee):
    def choose_action(self, meadow):
        return choice([Action.LEFT, Action.RIGHT, Action.UP, Action.DOWN])

class NeuralBee(Bee):
    visibility_radius = 1
    
    def __init__(self, max_capacity, network):
        Bee.__init__(self, max_capacity)
        self.network = network
    
    def choose_action(self, meadow):
        visible_objects = []
        for row_shift in range(-self.visibility_radius, self.visibility_radius + 1):
            for column_shift in range(-self.visibility_radius, self.visibility_radius + 1):
                x = self.position[0] + row_shift
                y = self.position[1] + column_shift
                
                visible_objects.append(meadow.meadow_objects[x][y])
       
        input_params = list(chain.from_iterable(map(NeuralBee._encode_meadow_object, visible_objects)))
        input_params.append(self.pollen_gathered / float(self.max_capacity))
        output = network.activate(input_params)
        maximum_output_index = list(output).index(max(output))
        
        return [Action.LEFT, Action.RIGHT, Action.UP, Action.DOWN][maximum_output_index]
    
    @staticmethod
    def _encode_meadow_object(meadow_object):
        encoding = {Grass: [0, 0, 0], Hive: [1, 0, 0], Flower: [0, 1, 0], Obstacle: [0, 0, 1]}
        return encoding[type(meadow_object)]
            
class Meadow(WorldObject):
    def __init__(self, meadow_objects):
        self.meadow_objects = meadow_objects
   
    def do_episode(self):
        for bee in self.bees:
            movement = bee.choose_action(self)
            next_position = (bee.position[0] + movement[0], bee.position[1] + movement[1])
            object_at_next_position = self.meadow_objects[next_position[0]][next_position[1]]
            if not issubclass(type(object_at_next_position), Obstacle):
                bee.position = next_position
                bee.interact_with(object_at_next_position)
    
    def reset_state(self):
        for obj in self.bees + list(chain.from_iterable(self.meadow_objects)):
            obj.reset_state()
                
    def __str__(self):
        bee_positions = set([bee.position for bee in self.bees])
        
        string = ""
        for x, row in enumerate(self.meadow_objects):
            for y, cell in enumerate(row):
                string += 'B' if (x, y) in bee_positions else str(cell)
            string += "\n"
        return string    
        
    
class RandomMeadow(Meadow):
    def __init__(self, width, height, obstacles_count, flowers_count, hive_count):
        meadow_objects = self._generate_meadow(width, height, obstacles_count, flowers_count, hive_count)
        self._add_borders(meadow_objects)
        self.hive_positions = list(self._find_hives_positions(meadow_objects))
        self.hives = [meadow_objects[position[0]][position[1]] for position in self.hive_positions]
        Meadow.__init__(self, meadow_objects)
    
    def set_bees(self, bees):
        for bee in bees:
            bee.initial_position = choice(self.hive_positions)
            bee.reset_state() 
        self.bees = bees
    
    def _find_hives_positions(self, meadow_objects):
        for x, row in enumerate(meadow_objects):
            for y, cell in enumerate(row):
                if issubclass(type(cell), Hive):
                    yield (x, y)
    
    def _add_borders(self, meadow_objects):
        for row in meadow_objects:
            row.insert(0, Obstacle())
            row.append(Obstacle())
        width = len(meadow_objects[0])
        obstacle_row = [Obstacle() for _ in range(0, width)]
        meadow_objects.insert(0, obstacle_row)
        meadow_objects.append(obstacle_row)       
        
    def _generate_meadow(self, width, height, obstacles_count, flowers_count, hive_count):
        obstacles = [Obstacle() for _ in range(0, obstacles_count)]
        flowers = [Flower(30) for _ in range(0, flowers_count)]
        hives = [Hive() for _ in range(0, hive_count)]
        grass = [Grass() for _ in range(0, width * height - obstacles_count - flowers_count - hive_count)]
        all_objects = obstacles + flowers + hives + grass
        shuffle(all_objects)
        return [all_objects[i * width : (i + 1) * width] for i in range(0, height)]

network = buildNetwork(28, 10, 4)      
meadow = RandomMeadow(10, 10, 10, 10, 1)

# class ManyEpisodesFitness(FitnessEvaluator):
#     def __init__(self, meadow):
#         self.meadow = meadow


        
def f(network):
    bees = [NeuralBee(5, network)]
    meadow.set_bees(bees)
    meadow.reset_state()
#     last_positions = [bee.position for bee in bees]
#     penalty_for_standing_still = 0
    for _ in range(1, 300):
        meadow.do_episode()
#         current_positions = [bee.position for bee in bees]
#         penalty_for_standing_still += sum([1 if a == b else 0 for a, b in zip(current_positions, last_positions)])
#         last_positions = current_positions
        
    return sum([hive.pollen for hive in meadow.hives])**2 + sum([bee.pollen_gathered for bee in bees]) #- penalty_for_standing_still
      
best = GA(f, network, maxEvaluations=500000).learn()

bees = [NeuralBee(5, best)]
meadow.set_bees(bees)
meadow.reset_state()
for _ in range(1, 300):
    print meadow
    meadow.do_episode()
    sleep(0.1)
