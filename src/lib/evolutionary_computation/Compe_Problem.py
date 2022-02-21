import numpy as np
import pandas as pd
from numpy import random

from lib.evolutionary_computation.Problem import Problem


class Compe_problem(Problem):

    def __init__(self,tracking,deepsort):
        self.tracking = tracking
        self.deepsort = deepsort
                        
        self.nObjectives = 1;
        
        self.ismax=False
        
        self.nVariables = deepsort["deepsort_cluster"].nunique()
                
        self.H_player_list = tracking.loc[tracking["player"].str.contains("H"),"player"].unique()
        self.V_player_list = tracking.loc[tracking["player"].str.contains("V"),"player"].unique()
        
        self.H_player_counts = len(self.H_player_list)
        self.V_player_counts = len(self.V_player_list)                
        self.divisions = [i+1 for i in range(self.H_player_counts)] + [-(i+1) for i in range(self.V_player_counts)]
        
        ## 距離
        self.eva = Distance_Evaluator(self.deepsort,self.tracking,self.H_player_list,self.V_player_list,isNorm=True)           
        
        self.SPF_evaluator = Same_Person_Per_Frame_Evaluator(self.deepsort);
        

    def initialize(self,solution):               
        solution_variables = random.randint(self.H_player_counts+self.V_player_counts,size = self.nVariables)
        solution_variables = solution_variables-self.V_player_counts
        solution.variables = np.where(solution_variables>=0,solution_variables+1,solution_variables)
        
        
               
    def evaluate(self,solution):
        #solution.objectives =  [self.eva.evaluate(solution.variables) + ]
        #solution.objectives =  [ self.eva.evaluate(solution.variables) + self.SPF_evaluator.evaluate(solution.variables)]

        solution.objectives =  [team_count(solution.variables,self.deepsort)+self.SPF_evaluator.evaluate(solution.variables)*100 + self.eva.evaluate(solution.variables)]



def team_count(solution_variable,deep_result):
    ret_val = 0
    
    
    home = np.where(solution_variable > 0)[0]
    visitor = np.where(solution_variable < 0)[0]
    
    if (not home.shape[0] == 0):

        home_team_count_list = deep_result.loc[deep_result["deepsort_cluster_encoded"].isin(home),"team"].value_counts()
        if(not 0 in home_team_count_list):
            home_team_count_list[0] = 0;
        if(not 1 in home_team_count_list):
            home_team_count_list[1] = 0;
        
        home_team1 = home_team_count_list[0]
        home_team2 = home_team_count_list[1]
        ret_val = ret_val + abs(home_team1-home_team2)
    
    if (not visitor.shape[0] == 0):
        visitor_team_count_list = deep_result.loc[deep_result["deepsort_cluster_encoded"].isin(visitor),"team"].value_counts()
        
        
        if(not 0 in visitor_team_count_list):
            visitor_team_count_list[0] = 0;
        if(not 1 in visitor_team_count_list):
            visitor_team_count_list[1] = 0;
            
        visitor_team1 = visitor_team_count_list[0]
        visitor_team2 = visitor_team_count_list[1]
        
        ret_val = ret_val + abs(visitor_team1-visitor_team2)
    
        
    return -1*ret_val


class Distance_Evaluator:
    
    def __init__(self,deep_result,tracking,H_player_list,V_player_list,isNorm=True):
        self.tracking = tracking.copy()
        self.deepsort = deep_result.copy();
        
        self.H_player_list = H_player_list
        self.V_player_list = V_player_list
        
        
        if (not self.deepsort["video"].nunique() == 1):
            raise Exception("multiple video files are found");
        
        self._view_mode();

        self.deepsort["m_x"] = self.deepsort["x"]*-1

        if (isNorm):
            self.deepsort["x"] = self._norm(self.deepsort["x"])
            self.deepsort["y"] = self._norm(self.deepsort["y"])  
            self.deepsort["m_x"] = self._norm(self.deepsort["m_x"])  
            
            
            self.tracking["x"] = self._norm(self.tracking["x"])
            self.tracking["y"] = self._norm(self.tracking["y"])                                    
            
            
        
        
        
        ## キャッシュ初期化
        self._init_cache()
        
        ## deep sort の各フレームに、対応するtrackingのフレーム(est_fram)を取得する。
        self._add_est_frame_to_deepsort();
        
    def _view_mode(self):
        view = self.deepsort["video"].unique()[0]
        if ("Endzone" in view):            
            self.tracking['x'], self.tracking['y'] = self.tracking['y'].copy(), self.tracking['x'].copy()

    def _get_Player(self,variable):
        if (variable > 0):
            return self.H_player_list[variable-1]
        else:
            return self.V_player_list[abs(variable)-1]
    
    
    def _init_cache(self):
        self.plus_cache = [{}]*self.deepsort["deepsort_cluster_encoded"].nunique()
        self.minus_cache = [{}]*self.deepsort["deepsort_cluster_encoded"].nunique()
        
    def _add_est_frame_to_deepsort(self):
        #self.tracking["est_frame"] = -99999;
        pd_list = [];
        
        for frame,each_df in self.deepsort.groupby("frame"):
            est_frame = self._find_nearest(self.tracking["est_frame"].values, frame)
            each_df["est_frame"] = est_frame

            pd_list.append(each_df)
        
        self.deepsort = pd.concat(pd_list)
        
        
    def _find_nearest(self,array,value):
        value = int(value)
        array = np.asarray(array).astype(int)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
    
    def _norm(self,x):
        b = x - x.min()
        b = b/b.max();
        return b;
        
    def evaluate(self,solution_variable):
        sol_val = list(solution_variable)
        ret_plus_val = 0
        ret_minus_val = 0

        for idx,val in enumerate(sol_val):            

            if ( val in self.plus_cache[idx].keys()):
                ret_plus_val = ret_plus_val + self.plus_cache[idx][val]
                ret_minus_val = ret_minus_val + self.minus_cache[idx][val]
                #ret_val = ret_val + self.cache[idx][val]
            else:                                                
                
                ## 指定した
                player = self._get_Player(val)                
                ext_deepsort = self.deepsort[self.deepsort["deepsort_cluster_encoded"] == idx];                                
                                                
                tracking_per_player = self.tracking[self.tracking["player"] == player]                                                
                tracking_per_player = tracking_per_player[tracking_per_player["est_frame"].isin(ext_deepsort["est_frame"].unique().tolist())]
                
                
                ## di
                x_dict = tracking_per_player.set_index("est_frame")["x"].to_dict()
                y_dict = tracking_per_player.set_index("est_frame")["y"].to_dict()                
                
                ext_deepsort["tracking_x"] = ext_deepsort["est_frame"].apply(lambda x: x_dict[x])                
                ext_deepsort["tracking_y"] = ext_deepsort["est_frame"].apply(lambda x: y_dict[x])    

                
                ext_deepsort["dist"] = np.sqrt((ext_deepsort["tracking_x"]-ext_deepsort["x"])**2 + (ext_deepsort["tracking_y"]-ext_deepsort["y"])**2)                
                ext_deepsort["m_dist"] = np.sqrt((ext_deepsort["tracking_x"]-ext_deepsort["m_x"])**2 + (ext_deepsort["tracking_y"]-ext_deepsort["y"])**2)                

                self.plus_cache[idx][val] = ext_deepsort["dist"].sum()
                self.minus_cache[idx][val] = ext_deepsort["m_dist"].sum()

                ret_plus_val = ret_plus_val + self.plus_cache[idx][val]
                ret_minus_val = ret_minus_val + self.minus_cache[idx][val]

        return min(ret_plus_val,ret_minus_val)
                



class Same_Person_Per_Frame_Evaluator:
    
    def __init__(self,deep_result):
        self.deep = deep_result.copy();
        self._erase_duplicated_per_frame();
        self._init_pivot();
    
    def _init_pivot(self):
        self.deep["dummy"] = 1;
        self.pivot = self.deep.pivot(index="frame",columns = "deepsort_cluster_encoded",values = "dummy").fillna(0)
        
        
    def _erase_duplicated_per_frame(self):
        pd_list = [];
        
        pd_list  = [each_df[~each_df["deepsort_cluster_encoded"].duplicated()] for key,each_df in  self.deep.groupby("frame")]
        self.deep = pd.concat(pd_list)
    
    def evaluate(self,variables):
        return -1* (self.pivot*variables).T.nunique().sum();
        
            
            
            