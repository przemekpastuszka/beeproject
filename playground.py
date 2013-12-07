'''
Created on Dec 7, 2013

@author: przemek
'''
from random import choice, shuffle
from time import sleep

class Action(object):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, 1)
    DOWN = (0, -1)

class Flower(object):
    def __init__(self, initial_capacity):
        self.initial_capacity = initial_capacity
        self.pollen = initial_capacity
    
    def __str__(self):
        return 'F' if self.pollen > 0 else 'X'

class Tulip(Flower):
    def __init__(self):
        Flower.__init__(self, 30)  

class Hive(object):
    def __init__(self):
        self.pollen = 0
        
    def __str__(self):
        return 'H'

class Obstacle(object):
    def __str__(self):
        return 'O'

class Grass(object):
    def __str__(self):
        return '.'

class Bee(object):
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.pollen_gathered = 0
    
    def choose_action(self, visible_objects):
        return choice([Action.LEFT, Action.RIGHT, Action.UP, Action.DOWN])
    
    def interact_with(self, meadow_object):
        if issubclass(type(meadow_object), Flower):
            pollen_to_gather = min(self.max_capacity - self.pollen_gathered, meadow_object.pollen)
            meadow_object.pollen -= pollen_to_gather
            self.pollen_gathered += pollen_to_gather
            
        if issubclass(type(meadow_object), Hive):
            meadow_object.pollen += self.pollen_gathered
            self.pollen_gathered = 0
            
    def __str__(self):
        return 'B'
            
class Meadow(object):
    def __init__(self, meadow_objects, bees):
        self.meadow_objects = meadow_objects
        self.bees = bees
   
    def do_episode(self):
        for bee in self.bees:
            movement = bee.choose_action(None) # implement me!
            next_position = (bee.position[0] + movement[0], bee.position[1] + movement[1])
            object_at_next_position = self.meadow_objects[next_position[0]][next_position[1]]
            if not issubclass(type(object_at_next_position), Obstacle):
                bee.position = next_position
                bee.interact_with(object_at_next_position)
                
    def __str__(self):
        bee_positions = set([bee.position for bee in self.bees])
        
        string = ""
        for x, row in enumerate(self.meadow_objects):
            for y, cell in enumerate(row):
                string += 'B' if (x, y) in bee_positions else str(cell)
            string += "\n"
        return string    
        
    
class RandomMeadow(Meadow):
    def __init__(self, width, height, obstacles_count, flowers_count, hive_count, bees):
        meadow_objects = self._generate_meadow(width, height, obstacles_count, flowers_count, hive_count)
        self._add_borders(meadow_objects)
        hive_positions = list(self._find_hives_positions(meadow_objects))
        self.hives = [meadow_objects[position[0]][position[1]] for position in hive_positions]
        for bee in bees:
            bee.position = choice(hive_positions) 
        Meadow.__init__(self, meadow_objects, bees)
    
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
        flowers = [Tulip() for _ in range(0, flowers_count)]
        hives = [Hive() for _ in range(0, hive_count)]
        grass = [Grass() for _ in range(0, width * height - obstacles_count - flowers_count - hive_count)]
        all_objects = obstacles + flowers + hives + grass
        shuffle(all_objects)
        return [all_objects[i * width : (i + 1) * width] for i in range(0, height)]
  
bees = [Bee(5) for _ in range(0, 3)] 
meadow = RandomMeadow(10, 10, 10, 10, 1, bees)

for i in range(1, 150):
    print meadow

    meadow.do_episode()
    sleep(0.1)

for hive in meadow.hives:
    print 'hive has: ', hive.pollen                 
for bee in bees:
    print 'bee has: ', bee.pollen_gathered
    
    