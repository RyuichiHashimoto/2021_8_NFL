from scipy.spatial.distance import cdist
from lib.noglobal import noglobal
import pandas as pd
import numpy as np

def closest_point(point,points,labels):
    return labels[cdist( [point],points).argmin()]   


@noglobal()
def erase_duplicated_deepsort_cluster(deepsort_result_per_video):
    target_df = deepsort_result_per_video.copy()


    pd_list =[];
    before_df = None;
    target_df["xy"] = [(x,y) for x,y in zip(target_df["x"],target_df["y"])];
    for frame, current_df in target_df.groupby("frame"):

        if (not current_df["deepsort_cluster"].isnull().sum() == 0):
            pd_list.append(current_df);
            continue;

        ## 初回のクラスターは無視
        if (before_df is None):
            before_df = current_df
            pd_list.append(current_df);
            continue;


        deepsort_cluster_count = current_df["deepsort_cluster"].value_counts()
        if (deepsort_cluster_count.max() >= 2):

            s = deepsort_cluster_count.to_dict()
            target_labels = [];
            not_duplicated_label = [];
            for key in s.keys():
                if (s[key] >1):
                    target_labels.append(key)
                else:
                    not_duplicated_label.append(key)


            before_loc_list = before_df["xy"].values.tolist()
            before_label_list = before_df["deepsort_cluster"].values.tolist()        

            each_pd_list = [];
            each_pd_list.append(current_df[~current_df["deepsort_cluster"].isin(target_labels)])        
            for label in target_labels:
                ext_df_per_label = current_df[current_df["deepsort_cluster"]==label]            
                ext_df_per_label["deepsort_cluster"] = [closest_point(x,before_loc_list,before_label_list) for x in ext_df_per_label["xy"]]
                each_pd_list.append(ext_df_per_label)
                #display(ext_df_per_label)


            tmp = pd.concat(each_pd_list)
            if (current_df.shape[0] == tmp.shape[0]):
                pd_list.append(tmp);
                before_df = tmp


                #tmp_each_df = tmp;
            else:
                print(current_df.shape[0] , tmp.shape[0])
                raise Exception("unexpeced error has occured")


        else:
            pd_list.append(current_df);
            before_df = current_df






            pass;
        
    
    
    return pd.concat(pd_list)