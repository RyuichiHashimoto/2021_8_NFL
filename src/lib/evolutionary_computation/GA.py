import numpy as np
from numpy import random


from lib.evolutionary_computation.Solution import Solution, population_objective_to_numpy
from lib.evolutionary_computation.Solution import population_to_numpy
from lib.multiprocess import exe_multiprocess_ret_as_list

from tqdm import tqdm




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


def flip_mutation_for_compe_base(variable_ndarray,problem,mutate_probability):
        
    change = random.randint(problem.H_player_counts+problem.V_player_counts, size =(variable_ndarray.shape[0], variable_ndarray.shape[1]))
    change = change - problem.V_player_counts
    change = np.where(change>=0,change+1,change)

    mutation_probability = np.random.rand(variable_ndarray.shape[0], variable_ndarray.shape[1])
        
    variable = np.where(mutation_probability<0.1,change,variable_ndarray)

    
    return variable



def gen_offsprings(population:list,problem):
    
    problem = population[0].problem
    
    ## parent selection
    parent1 = population_to_numpy(population)    
    parent2 = parent1.copy().T
    random.shuffle(parent2)
    parent2 = parent2.T
    
    
    ## offspring generation: ndarray
    offsprings_variables = uniform_crossover(parent1,parent2);    
    offsprings_variables = flip_mutation_for_compe_base(offsprings_variables,problem,mutate_probability = 1/problem.nVariables)
    
    offsprings = [];
    
    
    ## ndarray to solution list
    problem = population[0].problem
    arg = [[variable, problem]  for variable in offsprings_variables]
    

    offsprings = exe_multiprocess_ret_as_list(evaluate,arg,plot_processbar=False);

    
    """
    for variable in offsprings_variables:
        sol = Solution(problem)
        sol.variables = variable        
        problem.evaluate(sol)
        offsprings.append(sol)
    """
        
    return offsprings

def evaluate(one):
    variable = one[0]
    problem_ = one[1]
    
    sol = Solution(problem_)
    sol.variables = variable        
    problem_.evaluate(sol)
    return sol;


"""
def environmentalSelection(population,offspring):
    unionpopulation = [];
    unionpopulation.extend(population);
    unionpopulation.extend(offspring);
#    nondominatedSolution(unionpopulation);
    unionpopulation=sorted(unionpopulation);
    return unionpopulation[0:len(population)];
"""
def environmentalSelection(population,offspring):
    unionpopulation = [];
    unionpopulation.extend(population);
    unionpopulation.extend(offspring);
#    nondominatedSolution(unionpopulation);
    unionpopulation=sorted(unionpopulation);
    best_solution = unionpopulation[0]
    
    a = np.array([ (i+1)**2 for i in range(len(unionpopulation))]);
    probability = (a/np.sum(a))[::-1]


    return random.choice(unionpopulation, len(population),replace=False,p=probability), best_solution;



def exe_GA(problem):
    popsize = 100
    generations = 500
        
    poplations = initialize_population(problem,popsize);
    
    objective = [];
    best_solution = None;
    best_objective = 9999999;


    for gen in tqdm(range(generations)):
        offsprings = gen_offsprings(poplations,problem)
        poplations,best_tmp_solution = environmentalSelection(poplations,offsprings)
        #np.savetxt(f"population/{gen+1}_variable.csv", population_to_numpy(poplations,"variables").astype("int8"),delimiter=",",fmt='%.0e')        
        #np.savetxt(f"population/{gen+1}_objective.csv", population_to_numpy(poplations,"objectives"),delimiter=",",fmt='%.4e')

        if ( best_objective  >  best_tmp_solution.objectives[0]):
            best_solution = best_tmp_solution
            best_objective = best_solution.objectives[0]


        objective.append(best_objective)
        
    
    return poplations,objective,best_solution;    

if __name__ =="__main__":
    print("dummy start")