class Flower(object):
    def __init__(self, initial_capacity):
        self.pollen = initial_capacity

    def __str__(self):
        return 'F' if self.pollen > 0 else 'X'


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
