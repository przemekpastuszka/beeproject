from time import sleep
from pybrain.tools.shortcuts import buildNetwork
from genetic import genetic

from bees import NeuralBee
from meadow import MeadowFactory
import settings

class Fitness(object):
    def __init__(self, meadow_factory, bees_number, episodes, directions,
                 bee_capacity):
        self.meadow_factory = meadow_factory
        self.bees_number = bees_number
        self.episodes = episodes
        self.directions = directions
        self.bee_capacity = bee_capacity

    def __call__(self, network):
        meadow = meadow_factory.get_meadow()
        bees = [NeuralBee(self.bee_capacity,
                          network, meadow.hive_positions) for _ in range(self.bees_number)]
        meadow.set_bees(bees)
        for _ in range(self.episodes):
            meadow.do_episode(self.directions)
        return sum([hive.pollen for hive in meadow.hives])**2 +\
            sum([bee.pollen_gathered for bee in bees])


def create_brain(network_params, fitness, evaluations):
    network = buildNetwork(*network_params)
    
    def get_network_with(args):
        network._setParameters(args)
        return network
    
    best_params = genetic(lambda x: fitness(get_network_with(x)), len(network.params))
    return get_network_with(best_params)


if __name__ == "__main__":
    meadow_factory = MeadowFactory(settings.BOARD,
                                   settings.OBJECTS_DISTRIBUTION,
                                   settings.FLOWER_CAPACITY)
    meadow_factory.seed_meadow()
    fitness = Fitness(meadow_factory,
                      settings.BEES_NUMBER,
                      settings.EPISODES_PER_SIMULATION,
                      settings.DIRECTIONS,
                      settings.BEE_MAX_CAPACITY)
    brain = create_brain(settings.NETWORK_PARAMS, fitness,
                         settings.NETWORK_EVALUATIONS)
    meadow = meadow_factory.get_meadow()
    bees = [NeuralBee(settings.BEE_MAX_CAPACITY, brain, meadow.hive_positions) for _ in range(settings.BEES_NUMBER)]
    meadow.set_bees(bees)
    for _ in range(settings.EPISODES_PER_SIMULATION):
        print meadow
        meadow.do_episode(settings.DIRECTIONS)
        sleep(0.1)
