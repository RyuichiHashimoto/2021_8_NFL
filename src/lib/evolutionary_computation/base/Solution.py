import numpy as np



class Solution:
    
    def __init__(self,problem):
                
        self.problem = problem
        self.nObjectives = problem.nObjectives;
                        
        self.nVariables = problem.nVariables;
        
        self.variable_types = problem.variable_types
        
        self.divisions = problem.divisions

        self.ismax = problem.ismax
        
        
    ## This function assume that an optimization problem has a single objective function.
    def __lt__(self, other):
        return (self.ismax) == (self.objectives[0] > other.objectives[0]);


def population_to_numpy(population,type="variables"):
    if (type == "variables"):
        return population_variables_to_numpy(population);
    elif (type == "objectives"):
        return population_objective_to_numpy(population);
    else:
        raise Exception (f"unknown type is specified: {type}")
    





def population_variables_to_numpy(population):    
    return np.array([ individual.variables for individual in population ])

def population_objective_to_numpy(population):    
    return np.array([ individual.objectives for individual in population ])
    


