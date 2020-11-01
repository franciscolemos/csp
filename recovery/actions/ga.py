import numpy as np
from itertools import product
from deap import base, creator
import random
from deap import tools
import copy
from recovery.actions import feasibility
from recovery.actions import solution
from recovery.dal.classesDtype import gaType as gt
import pprint
class improvement:
    def __init__(self, flightRanges, rotationOriginal, index):
        flightCombinations = product(*flightRanges.values()) #all possible combination
        self.searchSpace = np.array(list(flightCombinations)) #convert the cross product to numpy array
        self.rotationOriginal = rotationOriginal
        self.index = index
        
        creator.create("FitnessMulti", base.Fitness, weights = gt.WEIGHTS) #min. noInfea, max. cancel., min. delay
        creator.create("Individual", list, fitness=creator.FitnessMulti)
        self.tb = base.Toolbox()
        self.tb.register("attribute", self.solGen) #function that generates an individual/solution
        self.tb.register("individual", tools.initRepeat, creator.Individual, self.tb.attribute, n = 1)
        self.tb.register("population", tools.initRepeat, list, self.tb.individual)
        self.tb.register("evaluate", self.evaluate)
        self.tb.register("mate", tools.cxTwoPoint)
        self.tb.register("mutate", self.mutate) #tools.mutFlipBit, indpb=0.05)
        self.tb.register("select", tools.selTournament, tournsize = gt.TOURN_SIZE)
        self._bestSol = []

    def solGen(self):
        size = len(self.searchSpace)
        num = random.randint(0, size-1)
        return tuple(self.searchSpace[num])

    def mutate(self, mutant):
        size = len(self.searchSpace)
        num = random.randint(0, size-1)
        #import pdb; pdb.set_trace()
        mutant[0] = tuple(self.searchSpace[num])
        return mutant,  #,

    def createPop(self):
        pop = self.tb.population(gt.IND_SIZE)
        return pop
    
    def evaluate(self, individual):
        rotation = copy.deepcopy(self.rotationOriginal) #keep a copy of the original because of new rotation
            #import pdb; pdb.set_trace()
        solution.newRotation(individual[0], rotation[self.index:]) #add the combo to the rotation
        rotationCopy = copy.deepcopy(rotation[rotation['cancelFlight'] != 1]) #only flights not cancelled in the copy
        rotationCopy = np.sort(rotationCopy, order = 'altDepInt')
        sizeInfCont = len(feasibility.continuity(rotationCopy))
        sizeInfTT = len(feasibility.TT(rotationCopy))
    
        noInf = sizeInfCont + sizeInfTT
        noCancel = sum([i for i in individual[0] if i == -1])
        delay = sum([i for i in individual[0] if i != -1])
        return noInf, noCancel, delay

    def bestSol(self, pop, _bestSol):
        pop.sort(key = lambda x: x.fitness, reverse =True)
        fits = [ind.fitness.values for ind in pop]
        popSol = pop[0][0] #first elem. of the pop.; best solution
        fitSol = fits[0] #first elem. of the fitnesses; fitness of the best solution
        if fitSol[0] == 0: #the new sol. is feasible
            #print("popSol: ", pop[0][0], "fitSol:", fitSol, "best sol: ", _bestSol)
            if fitSol[1] > _bestSol[1][1]: #compare noCancel from new best solution w/ curr. best sol. 0 > -1 less cancel.
                    _bestSol[0] = pop[0][0] #update sol.
                    _bestSol[1] = fitSol #upadate fitness
            if fitSol[1] == _bestSol[1][1]: #compare noCancel from new best solution w/ curr. best sol. 0 == 0 less cancel.
                if fitSol[2] < _bestSol[1][2]: #compare delay from new best solution w/ curr. best sol. 1140 < 1200
                    _bestSol[0] = pop[0][0] #update sol.
                    _bestSol[1] = fitSol #upadate fitness

            #import pdb; pdb.set_trace()
        return False
    
    def main(self):
        #import pdb; pdb.set_trace()
        self.pop = self.createPop()
        fitnesses = list(map(self.tb.evaluate, self.pop)) #calc. fitness for each ind. of the pop.
        for ind, fit in zip(self.pop, fitnesses): #match the fitness
            ind.fitness.values = fit

        fits = [ind.fitness.values for ind in self.pop] # Extracting all the fitnesses of 
        self._bestSol = [self.pop[0][0], fits[0]]
        g = 0
        while  g < gt.NO_GER: #max(fits) < 100 and
            g = g + 1 # A new generation
            print("-- Generation %i --" % g)
            offspring = self.tb.select(self.pop, len(self.pop)) # Select the next generation individuals
            offspring = list(map(self.tb.clone, offspring)) # Clone the selected individuals
            # Apply crossover on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < gt.CXPB:
                    self.tb.mate(list(child1[0]), list(child2[0]))
                    del child1.fitness.values
                    del child2.fitness.values
            # Apply mutation on the offspring
            for mutant in offspring:
                if random.random() < gt.MUTPB:
                    #import pdb; pdb.set_trace()
                    self.tb.mutate(mutant)
                    del mutant.fitness.values
            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.tb.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            self.pop[:] = offspring

            self.bestSol(self.pop, self._bestSol)
            print("Best sol.: ", self._bestSol)
            
        #import pdb; pdb.set_trace()
        return self._bestSol