import pandas as pd
import random
import numpy as np



def modified_merge_base_and_deepsort(base_sub,deepsort_sub,random_allocation=False,erase_duplicated=False):
    
    if (erase_duplicated == random_allocation):
        raise Exception("asdf");


    unique_player_list = base_sub["label"].unique().tolist()
    
    ret_df = deepsort_sub.copy()
    columns = ret_df.columns
        
    ## key列の追加
    ret_df["key"] = ret_df["video_frame"] + ret_df["left"].astype(str) + ret_df["width"].astype(str)+ ret_df["top"].astype(str) + ret_df["height"].astype(str)
    base_sub["key"] = base_sub["video_frame"] + base_sub["left"].astype(str) + base_sub["width"].astype(str)+ base_sub["top"].astype(str) + base_sub["height"].astype(str)
    ret_df["isDeepSpecuration"] = 1;
    base_sub["isDeepSpecuration"] = 0;
    
    pd_list = [];

    pd_list.append(ret_df);
    deepsort_key_list  = ret_df["key"].unique().tolist();    
    pd_list.append(base_sub[~base_sub["key"].isin(deepsort_key_list)]);
    
    ret_df = pd.concat(pd_list);
    
    if (erase_duplicated):
        bec = [];
        for key,each_df in ret_df.groupby("video_frame"):
            each_df = each_df.sort_values("isDeepSpecuration",ascending=False)
                        
            unique_df = each_df[~each_df.duplicated(subset="label",keep='first')]
            
            bec.append(unique_df)
    
        ret_df = pd.concat(bec)
        
    
    
    if (random_allocation):
        bec = [];
        for key,each_df in ret_df.groupby("video_frame"):
            each_df = each_df.sort_values("isDeepSpecuration",ascending=False)
                        
            unique_df = each_df[~each_df.duplicated(subset="label",keep='first')]
            duplicated_df = each_df[each_df.duplicated(subset="label",keep='first')]
            
            notcandidate = unique_df["label"].unique().tolist()
            candidate_df = [ ele   for ele in unique_player_list if (ele not in notcandidate) ]                        
            
            sample = random.sample(candidate_df, duplicated_df.shape[0])
            
            if ( len(sample) != 0):
                duplicated_df["label"] = sample
                unique_df = unique_df.append(duplicated_df)
            
            bec.append(unique_df)
    
        ret_df = pd.concat(bec)
    
    
    
    
    
    
    return ret_df;







def merge_base_and_deepsort(base_sub,deepsort_sub, erase_duplicated = False,random_allocation=False):
    if (erase_duplicated and random_allocation):
        raise Exception("asdf")
    
    
    unique_player_list = base_sub["label"].unique().tolist()
    
    ret_df = base_sub.copy()
    columns = ret_df.columns
        
    ## key列の追加
    deepsort_sub["key"] = deepsort_sub["video_frame"] + deepsort_sub["left"].astype(str) + deepsort_sub["width"].astype(str)+ deepsort_sub["top"].astype(str) + deepsort_sub["height"].astype(str)
    ret_df["key"] = ret_df["video_frame"] + ret_df["left"].astype(str) + ret_df["width"].astype(str)+ ret_df["top"].astype(str) + ret_df["height"].astype(str)
    
    ## deepsortの推定結果をhashmapに加える。
    deepsort_expectation_hashmap = {};
    for key,label in zip(deepsort_sub["key"],deepsort_sub["label"]):
        deepsort_expectation_hashmap[key] = label
        
    ret_df["label"] = ret_df.apply(lambda x:  deepsort_expectation_hashmap[x["key"]] if (x["key"] in deepsort_expectation_hashmap.keys()) else x["label"] ,axis=1)
    ## 1: Deepsort result, 0: base_sub result
    ret_df["isDeepSpecuration"] = ret_df.apply(lambda x:  1 if (x["key"] in deepsort_expectation_hashmap.keys()) else 0,axis=1)
    
    
    if (erase_duplicated):
        bec = [];
        for key,each_df in ret_df.groupby("video_frame"):
            each_df = each_df.sort_values("isDeepSpecuration")
                        
            unique_df = each_df[~each_df.duplicated(subset="label",keep='first')]
            
            bec.append(unique_df)
    
        ret_df = pd.concat(bec)
        
    
    
    if (random_allocation):
        bec = [];
        for key,each_df in ret_df.groupby("video_frame"):
            each_df = each_df.sort_values("isDeepSpecuration")
                        
            unique_df = each_df[~each_df.duplicated(subset="label",keep='first')]
            duplicated_df = each_df[each_df.duplicated(subset="label",keep='first')]
            
            notcandidate = unique_df["label"].unique().tolist()
            candidate_df = [ ele   for ele in unique_player_list if (ele not in notcandidate) ]                        
            
            sample = random.sample(candidate_df, duplicated_df.shape[0])
            
            if ( len(sample) != 0):
                duplicated_df["label"] = sample
                unique_df = unique_df.append(duplicated_df)
            
            bec.append(unique_df)
    
        ret_df = pd.concat(bec)
    
    
    deepsort_sub = deepsort_sub.drop("key",axis=1)
    ret_df = ret_df.drop("key",axis=1)
    
    return ret_df;
