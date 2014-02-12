'''
Created on 27-12-2013

@author: pastuszka
'''

from random import shuffle, randrange, sample, random, gauss

def genetic(fitness_function, individual_size):
    population_size = 30
    stagnation_threshold = 5
    population = [list([gauss(0, 1) for _ in range(individual_size)]) for _ in range(0, population_size)]
        
    population_with_fitness = evaluate_fitness(population, fitness_function)
    last_best_fitness = choose_best(population_with_fitness)[1]
    stagnation = 0
    iterations = 0
    while stagnation < stagnation_threshold:
        parents = choose_parents(population_with_fitness)
        children = breed(parents)
        mutate(children)
        population_with_fitness = merge(population_with_fitness, evaluate_fitness(children, fitness_function))
        
        current_best_fitness = population_with_fitness[0][1]
        if current_best_fitness <= last_best_fitness:
            stagnation += 1
        else:
            stagnation= 0    
            last_best_fitness = current_best_fitness
        iterations += 1
    
    best_individual = choose_best(population_with_fitness)
    print "Genetic algorithm stopped after ", iterations, " iterations with fitness: ", best_individual[1]        
    return best_individual[0]

def evaluate_fitness(population, fitness_function):
    return [(individual, fitness_function(individual)) for individual in population]

def choose_parents(population):
    parents = []
    for _ in xrange(0, len(population)):
        tournament = sample(population, 5)
        parents.append(choose_best(tournament))
        
    return parents

def breed(parents):
    shuffle(parents)
    children = []
    for i in range(1, len(parents), 2):
        children += crossover(parents[i - 1][0], parents[i][0])
    return children

def crossover(a, b):
    length = len(a)
    left = randrange(0, length + 1)
    right = randrange(left, length + 1)
    
    return [a[0:left] + b[left:right] + a[right:length + 1], b[0:left] + a[left:right] + b[right:length + 1]]

# def crossoverOld(x, y):
#     childA = []
#     childB = []
#     
#     for a, b in zip(x, y):
#         if random() < 0.5:
#             childA.append(a)
#             childB.append(b)
#         else:
#             childA.append(b)
#             childB.append(a)
#             
#     return [childA, childB]

def mutate(children):
    for child in children:
        for i in range(len(child)):
            if random() <= 1.0/len(child):
                child[i] += gauss(0, 0.2)

def merge(parents, children):
    both = parents + children
    both.sort(key=lambda x: -x[1])
    return both[:len(parents)]

def choose_best(population):
    return max(population, key=lambda x: x[1])
    
   
        
    