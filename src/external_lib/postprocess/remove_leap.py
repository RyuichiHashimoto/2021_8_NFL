import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import random

class remove_leap:
    
    def __init__(self,submission_df,parameter=15,verbose=False):
        self.df = submission_df.copy();
        self.columns = self.df.columns;
        self.theshold = parameter
        self.verbose= verbose;
        
        
    def _prepare(self):
        
        ### ヘルメットの位置を推定
        self.df["x"] = self.df["left"]  + self.df["width"]/2
        self.df["y"] = self.df["top"]  + self.df["height"]/2
        self.df["xy"] = [ np.array([x,y]) for x,y in zip(self.df["x"],self.df["y"])];
        
        
        ## 各フレームを行、各ラベルの値（H22）を列、要素は画像内のヘルメットの位置
        self.pivot_df = self.df.pivot(index = "frame",columns="label",values = "xy")
        
        
        ## 一つ前のフレームの同じplayer ラベルとの距離を算出
        self.prev_pivot_df = self.pivot_df.shift(1)
        self.dif_pivot_df = self.pivot_df - self.prev_pivot_df
        
        
        self.player_cols = []
        self.distance_cols = [];
        self.exchangeflag_cols = [];

                
        for col in self.dif_pivot_df.columns:                
            self.dif_pivot_df[col+"_distance_bet_prev"] = self.dif_pivot_df[col].apply(lambda x:np.linalg.norm(x) if type(x) == np.ndarray else -1).fillna(-1)    
            self.dif_pivot_df[col + "_exchangeflag"] = self.dif_pivot_df[col+"_distance_bet_prev"]>self.theshold

            self.exchangeflag_cols.append(col + "_exchangeflag")
            self.distance_cols.append(col+"_distance_bet_prev")

        self.dif_pivot_df["isOK"] = self.dif_pivot_df[self.exchangeflag_cols].sum(axis=1)
    

        added_union_sub_pivot_df = self.pivot_df.add_suffix("_current_pos")
        added_prev_Union_sub_pivot_df = self.prev_pivot_df.add_suffix("_prev_pos")
        
        ## 「該当のフレーム」と「その一つ前のフレーム」のヘルメットの位置および、そのその差分を算出
        self.dif_pivot_df = pd.concat([self.dif_pivot_df,added_union_sub_pivot_df,added_prev_Union_sub_pivot_df],axis=1)        
        
        
   
    def _find_exchanged_player_per_frame(self,current_series,prev_series):        
        target_players_candidate = current_series[self.exchangeflag_cols];
        target_players = [];


        ## ラベルの交換候補となるplayerを抽出
        for col,val in target_players_candidate.items():
            if (val):
                target_players.append(col.split("_")[0])

        
        
        ## ラベル交換候補のplayerの位置を取得するためのカラム名を取得
        target_pos = [ i+"_current_pos" for i in target_players]

        ## 交換対象となるplayerの「現在」および「一つ前のフレーム」のときのヘルメットの位置を取得
        current_player_pos = list(current_series[target_pos])        
        prev_player_pos = list(prev_series[target_pos])

        ## 距離行列計算をするため、一つ上のものをnumpy.arrayに変更する。
        current_pos_list = np.array(current_player_pos)
        prev_pos_list = np.array(prev_player_pos)

        ### current_pos_numpyとprev_pos_numpyによる距離行列    
        distance_matrix = cdist(current_pos_list,prev_pos_list,metric="euclidean");

        ### 各距離行列でprev_pos_numpyから最も近い位置にあるcurrent_pos_numpyの点の番号を取得
        minimum_dis_index = list(np.argmin(distance_matrix, axis=0));

        
        if (len(minimum_dis_index) == len(np.unique(minimum_dis_index))):        
            ## 現在と一つ前のフレームの各playerが1対1で対応した場合。
            ret_list =  minimum_dis_index;        
        else:        
            ret_hashmap = {}

            ## 重複して割り当てられたcurrent_pos_listの点の番号
            duplicated_assign_candidate = [];

            ## 現状割り当てられていないcurrent_pos_listの点の番号
            not_assign_candidate = [];
            
            
            for key in range(len(minimum_dis_index)):                                                
                if (minimum_dis_index.count(key) == 1):                
                    s = minimum_dis_index.index(key)                
                    ret_hashmap[s] = key                
                elif (minimum_dis_index.count(key) == 0):                
                    not_assign_candidate.append(key);
                else:                
                    duplicated_assign_candidate.append(key);

            ## 各重複要素(previousの点)ごとに、その重複要素に最もあうcurrentの点を探索
            ## (該当重複要素との距離が最短のcurrentを見つける。)
            for dup_candidate in duplicated_assign_candidate:

                ## 該当重複要素が最短のcurrentの点のリスト
                dup_target = [ind for ind,x in enumerate(minimum_dis_index) if x == dup_candidate ]        

                ## previousとの距離が最短のcurrentの点
                min_index = np.argmin(distance_matrix[dup_candidate,dup_target])                       

                ret_hashmap[dup_target.pop(min_index)] = dup_candidate                                    

                ## その他の点はランダムに割当
                for dup in  dup_target:
                    ret_hashmap[dup] = not_assign_candidate.pop(random.randint(0, len(not_assign_candidate)-1))



            ret_list = [ret_hashmap[key] for key in range(len(minimum_dis_index))]


            if (self.verbose):
                print("----------------------------")
                display(current_pos_list)
                display(prev_pos_list)
                display(distance_matrix)
                print("before",minimum_dis_index)
                print("after",ret_list)




        ret_hash = {}
        for ind,k in enumerate(ret_list):
            before_pos = target_pos[ind].split("_")[0]
            after_pos = target_pos[ret_list[ind]].split("_")[0]            
            ret_hash[before_pos] = after_pos + "_______"

        return ret_hash
    

    def execute(self):        
        
        pd_list = []
        before_series = None;
        change_hashmap_list =[]
        for index,each_series in self.dif_pivot_df.iterrows():        

            Leap_counts = each_series["isOK"]                         

            if (Leap_counts < 2):
                pass;
            elif(Leap_counts >= 2):
                change_hashmap = self._find_exchanged_player_per_frame(each_series,before_series);
                change_hashmap_list.append([index,change_hashmap])
            else:
                raise Exception("unexpected error has occurred");

            before_series = each_series;
            
            
        change_target = change_hashmap_list.copy()
        pd_list = [];

        for key,each_df in self.df.copy().groupby("frame"):
            ind = key+1;
    
            if ( (len(change_target) > 0) and change_target[0][0] ==  ind ):
                s = change_target.pop(0)

                modified = each_df.replace({"label":s[1]})
                modified["label"] = modified["label"].str.replace("_______","")
                pd_list.append(modified)
            else:
                pd_list.append(each_df)

        return pd.concat(pd_list)[self.columns]
            
if __name__ == "__main__":
    s = remove_leap(sub,parameter=5)
    s._prepare();
    sub = s.execute()
    