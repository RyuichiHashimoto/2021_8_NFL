from lib.noglobal import noglobal
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.spatial.distance import cdist
from scipy import stats



@noglobal()
def find_nearest(array, value):
    value = int(value)
    array = np.asarray(array).astype(int)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

@noglobal()
def calc_speaman(target_label,target_neighbor_player_list,tracking_neighbor_player_list_hash):
    
    deepsort_rank = np.argsort([ int(s[1:]) if ("H" in s) else -1 *int(s[1:]) for s in target_neighbor_player_list]);
    #print(deepsort_rank)
    #print(tracking_neighbor_player_list_hash)
    
    ret_list =[]
    
    for key in tracking_neighbor_player_list_hash.keys():                    
        neeighbor_rank =  np.argsort([ int(s[1:]) if ("H" in s) else -1 *int(s[1:])  for s in tracking_neighbor_player_list_hash[key]]) 
        
        rho,pval =  stats.spearmanr(deepsort_rank,neeighbor_rank)
        
        ret_list.append([rho,key,target_label]);
        
    ret_list = sorted(ret_list,reverse=True);
    return ret_list
   
@noglobal()
def assign(score_list,n_of_assign_player):
    
    
    found_deepsort_label_list =[];
    assigned_player_list =[];
    ret_hash = {};
    for score in score_list:
        if (( not score[1] in assigned_player_list) and (not score[2] in found_deepsort_label_list)):
            ret_hash[score[2]] = score[1];
            
            assigned_player_list.append(score[1]);
            found_deepsort_label_list.append(score[2]);
        
        
            if (len(assigned_player_list)==n_of_assign_player):
                return ret_hash
            
        
        
    raise Exception("unexpected error has occured");
    


@noglobal()
def re_assign_label_per_deepsort_cluster(deepsort_result,trackings):
            
    final_result =  deepsort_result.copy()
    column = final_result.columns
    
    final_result["game_play"] = final_result["video"].apply(lambda x: "_".join(x.split("_")[:2]))
    max_frame = final_result["frame"].max()
    video = final_result["game_play"].unique()[0]
    
    ext_tracking = trackings[trackings["game_play"] == video]
    ext_tracking = ext_tracking[ext_tracking["est_frame"] < max_frame+3]
    ext_tracking["xy"] = [(x,y) for x,y in zip(ext_tracking["x"],ext_tracking["y"])]
    
    
    ## Step 1
    pd_list =[];


    for frame,each_df in tqdm(final_result.groupby("frame")):
      
        
        ## label_deepsortが重複しているレコードを抽出
        duplicated_df = each_df[each_df.duplicated(subset="label",keep=False)]
        

        
        ## 重複ラベルがない場合
        if (duplicated_df.shape[0]==0):        
            pd_list.append(each_df);
        else:
            

            ## 該当フレームに近いtracking情報を抽出
            est_frame = find_nearest(ext_tracking["est_frame"].values, frame)
            tracking_per_frame = ext_tracking[ext_tracking['est_frame']==est_frame]


            ## label_deepsortが重複していないラベルを抽出
            not_duplicated_df = each_df[~each_df.duplicated(subset="label",keep=False)].reset_index(drop=True)        

            ## 確定しているプレイヤーのリスト(Deepsort)        
            found_players_list = not_duplicated_df["label"].unique().tolist()        

            counter = 0
            for label_deepsort, df_per_label_deepsort in duplicated_df.groupby("label"):

                ## 重複原因がdeepsort_clusterによるものなら、無視する。            
                if (df_per_label_deepsort["deepsort_cluster"].nunique() == 1):

                    pd_list.append(df_per_label_deepsort);                            
                    counter = counter + df_per_label_deepsort.shape[0]
                else:
                    ## 異なるDeepsortクラスターが同じプレイヤーを指していた場合


                    ## 重複するdeepsortクラスターを一つにする。
                    ## (deepsort_clusterが同じ点は近接であると仮定)
                    df_per_label_deepsort = df_per_label_deepsort[~df_per_label_deepsort.duplicated(subset=["label","deepsort_cluster"],keep="first")]


                    ### 残りは追加用として用意
                    add = df_per_label_deepsort[df_per_label_deepsort.duplicated(subset=["label","deepsort_cluster"],keep="first")]

                    ## 確定していないプレイヤーデータセット(Tracking)
                    tracking_not_found_player_list = tracking_per_frame[~tracking_per_frame["player"].isin(found_players_list)]                                


                    ## 確定している
                    tracking_found_player_df = tracking_per_frame[tracking_per_frame["player"].isin(found_players_list)].reset_index(drop=True)
                    tracking_found_player_position_list = tracking_found_player_df["xy"].values.tolist();

                    #print(len(tracking_found_player_position_list))

                    ## key:確定していないプレイヤー
                    ## value: 確定しているプレイヤー（距離の観点で昇順にソート）
                    tracking_candidate_hashmap = {};
                    for key,tracking_each_player  in tracking_not_found_player_list.iterrows():
                        dist_list = cdist([tracking_each_player["xy"]],tracking_found_player_position_list)[0]                    
                        index_list = np.argsort(dist_list)                    
                        tracking_candidate_hashmap[tracking_each_player["player"]] = tracking_found_player_df.loc[index_list,"player"].tolist()

                    first_non_nan_loc_list = not_duplicated_df["xy"].values.tolist()
                    #print(len(tracking_found_player_position_list))


                    deepsort_hashmap = {};
                    for key,each_person_per_label_deepsort in df_per_label_deepsort.iterrows():
                        dist_list = cdist([each_person_per_label_deepsort["xy"]],first_non_nan_loc_list)[0]                                    
                        index_list = np.argsort(dist_list)
                        label_list = not_duplicated_df.loc[index_list,"label"].tolist()

                        deepsort_hashmap[each_person_per_label_deepsort["deepsort_cluster"]] = label_list                    




                    assign_info = [];
                    for key in deepsort_hashmap.keys():
                        nearest_player_info_per_deepsort_cluster = deepsort_hashmap[key]
                        tmp = calc_speaman(key,nearest_player_info_per_deepsort_cluster,tracking_candidate_hashmap);
                        assign_info = assign_info + tmp;


                    replace_info = assign(assign_info,len(deepsort_hashmap));

                    df_per_label_deepsort["label"] = df_per_label_deepsort["deepsort_cluster"].apply(lambda x:replace_info[x]);
                    pd_list.append(add)
                    pd_list.append(df_per_label_deepsort)
                    counter = counter + add.shape[0] + df_per_label_deepsort.shape[0]

                                                                    
            ## 先に合わせておく
            pd_list.append(not_duplicated_df);        
            
    s = pd.concat(pd_list)[column]
    
    return s

#b = re_assign_label_per_deepsort_cluster(final_result,trackings)
