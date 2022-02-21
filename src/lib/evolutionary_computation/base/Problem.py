from abc import ABC,abstractmethod
import numpy as np
from numpy import random


class Problem(ABC):
    
    def __init__(self):
        
        
        pass;
    
    @abstractmethod
    def evaluate(self,variables):
        raise notImplementYet();
        
    
    def get_nObjectives(self):
        return self.nObjectives;
    
    def get_nVariables(self):
        return self.nVariables;
    
    def get_variabletypes(self):
        return self.variable_types    
    
    def get_variable_range(self):
        return self.variable_range
    


class knapsackProblem(Problem):

    def __init__(self):
        self.nObjectives = 1;
        self.nVariables = 500;
        self.variable_types = 5;
        self.divisions = [2]*self.nVariables
        self.ismax=True

        self.weights = random.randint(51, size =self.nVariables) + 50
        self.profit = random.randint(51, size =self.nVariables) + 50
        self.capacity = sum(self.weights)/2;



        
               
    def evaluate(self,solution):
        kanpassck_weight = solution.variables.T@self.weights
        
        if (kanpassck_weight > self.capacity):
            solution.objectives = np.array([-999]);
        else:
            sum_ = solution.variables.T@self.profit
            solution.objectives = np.array([sum_]);


        
        


    def initialize(self,solution):               
        solution.variables = np.array([random.randint(0,solution.divisions[i])  for i in range(solution.nVariables)])
        





class onemaxProblem(Problem):

    def __init__(self):
        self.nObjectives = 1;
        self.nVariables = 5;
        self.variable_types = 5;
        self.divisions = [5]*5
        self.ismax=True
        
               
    def evaluate(self,solution):
        sum_ = np.sum(solution.variables);        
        solution.objectives = np.array([sum_]);
        

    def initialize(self,solution):       
        solution.variables = np.array([random.randint(0,solution.divisions[i])  for i in range(solution.nVariables)])



class zeromaxProblem(Problem):

    def __init__(self):
        self.nObjectives = 1;
        self.nVariables = 5;
        self.variable_types = 5;
        self.divisions = [5]*5
        self.ismax=False

        
               
    def evaluate(self,solution):
        sum_ = np.sum(solution.variables);        
        solution.objectives = np.array([sum_]);
        

    def initialize(self,solution):       
        solution.variables = np.array([random.randint(0,solution.divisions[i])  for i in range(solution.nVariables)])