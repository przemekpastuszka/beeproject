from time import sleep
from network import Network
from genetic import genetic

from bees import NeuralBee
from meadow import MeadowFactory
import settings

class Fitness(object):
    def __init__(self, meadow_factory, bees_number, episodes, directions,
                 bee_capacity):
        self.bees_number = bees_number
        self.episodes = episodes
        self.directions = directions
        self.bee_capacity = bee_capacity
        self.meadow = meadow_factory.get_meadow()

    def __call__(self, network):
        self.meadow = meadow_factory.get_meadow()
        bees = [NeuralBee(self.bee_capacity,
                          network, self.meadow.hive_positions) for _ in range(self.bees_number)]
        self.meadow.set_bees(bees)
        for _ in range(self.episodes):
            self.meadow.do_episode(self.directions)
        return sum([hive.pollen for hive in self.meadow.hives])**2 +\
            sum([bee.pollen_gathered for bee in bees])


def create_brain(network_params, fitness, evaluations):
    network = Network(network_params.inputs, network_params.hidden_neurons, network_params.outputs)
    
    def get_network_with(args):
        network.set_params(args)
        return network
    
    best_params = genetic(lambda x: fitness(get_network_with(x)), network.number_of_params())
    return get_network_with(best_params)


if __name__ == "__main__":
#     import cProfile, pstats, StringIO
#     pr = cProfile.Profile()
#     pr.enable()
    
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
    meadow = fitness.meadow
    
#     pr.disable()
#     s = StringIO.StringIO()
#     sortby = 'cumulative'
#     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#     ps.print_stats()
#     print s.getvalue()
    bees = [NeuralBee(settings.BEE_MAX_CAPACITY, brain, meadow.hive_positions) for _ in range(settings.BEES_NUMBER)]
    meadow.set_bees(bees)
    for _ in range(settings.EPISODES_PER_SIMULATION):
        print meadow
        meadow.do_episode(settings.DIRECTIONS)
        sleep(0.1)
