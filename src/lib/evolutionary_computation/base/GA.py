import numpy as np
from numpy import random
from lib.evolutionary_computation.Solution import Solution
from lib.evolutionary_computation.Solution import population_to_numpy





def initialize_population(problem,populationsize):
    retpop = [ Solution(problem)  for i in range(populationsize)];
    
    for sol in retpop:
        problem.initialize(sol);
        problem.evaluate(sol);
        
    
    return retpop





def uniform_crossover(pop1_variables,pop2_variables):
    if ( not ( (pop1_variables.shape[0] == pop2_variables.shape[0]) and (pop1_variables.shape[1] == pop2_variables.shape[1]))):        
        raise Exception(f"The shape is wrong between ,{parent1.shape} and {parent2.shape}")
    
    
    random_variable = np.random.rand(pop1_variables.shape[0], pop1_variables.shape[1])
    random_variable = np.where(random_variable > 0.5,1,0)
    return  pop1_variables*random_variable + pop2_variables*(1-random_variable);

def flip_mutation(variable_ndarray,divisions,mutate_probability):
    
    change = random.randint(divisions, size =(variable_ndarray.shape[0], variable_ndarray.shape[1]))
    
    mutation_probability = np.random.rand(variable_ndarray.shape[0], variable_ndarray.shape[1])    
    mutation_probability = np.where(mutation_probability < mutate_probability,1,0)
    
    mutate_rotation = mutation_probability*change    
    variable = (variable_ndarray + mutate_rotation)%divisions
    
    return variable



def gen_offsprings(population:list):
    
    problem = population[0].problem
    
    ## parent selection
    parent1 = population_to_numpy(population)    
    parent2 = parent1.copy().T
    random.shuffle(parent2)
    parent2 = parent2.T
    
    
    ## offspring generation: ndarray
    offsprings_variables = uniform_crossover(parent1,parent2);    
    offsprings_variables = flip_mutation(offsprings_variables,divisions = problem.divisions,mutate_probability = 1/problem.nVariables)
    
    offsprings = [];
    
    
    ## ndarray to solution list
    problem = population[0].problem
    for variable in offsprings_variables:
        sol = Solution(problem)
        sol.variables = variable        
        problem.evaluate(sol)
        offsprings.append(sol)
        
    return offsprings
        

def environmentalSelection(population,offspring):
    unionpopulation = [];
    unionpopulation.extend(population);
    unionpopulation.extend(offspring);
#    nondominatedSolution(unionpopulation);
    unionpopulation=sorted(unionpopulation);
    return unionpopulation[0:len(population)];



def exe_GA(problem):
    popsize = 100
    generations = 500
        
    poplations = initialize_population(problem,popsize);
    
    for gen in range(generations):
        offsprings = gen_offsprings(poplations)
        poplations = environmentalSelection(poplations,offsprings)
        
    
    return poplations;    

if __name__ =="__main__":
    print("dummy start")