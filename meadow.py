from random import choice, shuffle
from copy import deepcopy
from collections import namedtuple

from world_objects import Flower, Hive, Obstacle, Grass


class MeadowFactory(namedtuple('MeadowFactory',
                               ['board',
                                'objects_distribution',
                                'flower_capacity'])):
    def seed_meadow(self):
        self.random_meadow = RandomMeadow(*self)

    def get_meadow(self):
        return deepcopy(self.random_meadow)


class RandomMeadow(object):
    def __init__(self, board, objects_distribution, flower_capacity):
        self.meadow_objects = self._generate_meadow(board,
                                                    objects_distribution,
                                                    flower_capacity)
        self._add_borders()
        self._add_borders()
        self.hives, self.hive_positions = self._find_hives()

    def do_episode(self, directions):
        """
           Triggers bee's single step. For all bees - one by one.
        """
        for bee in self.bees:
            movement = bee.choose_action(self, directions, self.bees)
            next_position = (bee.position[0] + movement[0],
                             bee.position[1] + movement[1])
            object_at_next_position =\
                self.meadow_objects[next_position[0]][next_position[1]]
            if not isinstance(object_at_next_position, Obstacle):
                bee.position = next_position
                bee.interact_with(object_at_next_position)

    def set_bees(self, bees):
        """
            Randomly assign bees to starting points being hive positions
        """
        for bee in bees:
            bee.position = choice(self.hive_positions)
        self.bees = bees

    def _find_hives(self):
        hives = []
        positions = []
        for x, row in enumerate(self.meadow_objects):
            for y, cell in enumerate(row):
                if isinstance(cell, Hive):
                    hives.append(cell)
                    positions.append((x, y))
        return hives, positions

    def _add_borders(self):
        """
            Surrounds current meadow with Obstacles.
        """
        for row in self.meadow_objects:
            row.insert(0, Obstacle())
            row.append(Obstacle())
        width = len(self.meadow_objects[0])
        obstacle_row = [Obstacle() for _ in range(width)]
        self.meadow_objects.insert(0, obstacle_row)
        self.meadow_objects.append(obstacle_row)

    def _generate_meadow(self, board, distribution, flower_capacity):
        """
            Generates random meadow of width and height specified, containing
            given number of world objects.

            rtype: 2-dimensional array of world objects
        """
        obstacles = [Obstacle() for _ in range(distribution.obstacles)]
        flowers =\
            [Flower(flower_capacity) for _ in range(distribution.flowers)]
        hives = [Hive() for _ in range(distribution.hives)]
        grass = [Grass() for _ in range(board.remaining_space(distribution))]
        all_objects = obstacles + flowers + hives + grass
        shuffle(all_objects)
        return self._get_multidimensional_meadow(board, all_objects)

    def _get_multidimensional_meadow(self, dimensions, objects):
        return self._dimensionalize_meadow(dimensions, objects,
                                           0, len(objects))

    def _dimensionalize_meadow(self, dimensions, objects, start, stop):
        """
           Recursively splits flat list to nested lists of length
           defined by dimensions parameter.
        """
        if len(dimensions) == 1:
            return objects[start:stop]
        step = (stop - start) / dimensions[0]
        return [
            self._dimensionalize_meadow(
                dimensions[1:], objects,
                start + i * step, start + (i + 1) * step
            ) for i in range(dimensions[0])
        ]

    def __str__(self):
        """
           Returns Meadow graphical representation as a list of meadow objects'
           graphical representations
        """
        bee_positions = set([bee.position for bee in self.bees])

        string = ""
        for x, row in enumerate(self.meadow_objects):
            for y, cell in enumerate(row):
                string += 'B' if (x, y) in bee_positions else str(cell)
            string += "\n"
        return string
