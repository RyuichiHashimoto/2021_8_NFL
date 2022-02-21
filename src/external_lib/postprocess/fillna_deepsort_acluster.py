from scipy.spatial.distance import cdist
from lib.noglobal import noglobal

import pandas as pd

@noglobal()
def closest_point(point,points,labels):
    return labels[cdist( [point],points).argmin()]   


@noglobal()
def fillnan_first_frame(ret_df):        
    target_df = ret_df.copy() 
    target_df["xy"] = [ (x,y) for x,y in zip(target_df["x"],target_df["y"])];
    minimum_frame = target_df.dropna(subset=["deepsort_cluster"])["frame"].min()
    first_non_nan_df = target_df[target_df["frame"] == minimum_frame];
    first_non_nan_loc_list = first_non_nan_df["xy"].values.tolist()
    first_non_nan_label_list = first_non_nan_df["deepsort_cluster"].values.tolist()

    pd_list = [];

    for frame, df_per_frame in target_df.groupby("frame"):

        if (frame < minimum_frame):

            list_per_frame = [];
            for ind, record in df_per_frame.iterrows():
                record["deepsort_cluster"] = closest_point(record["xy"],first_non_nan_loc_list,first_non_nan_label_list) 
                list_per_frame.append(record)









            modified_df = pd.concat(list_per_frame,axis=1).T;        
            if (modified_df.shape[0] != df_per_frame.shape[0]):
                print(modified_df.shape[0],df_per_frame.shape[0])
                raise Exception("adsf")
            pd_list.append(modified_df)


        else:

            pd_list.append(df_per_frame);
        
    return pd.concat(pd_list)
            
#result_df = fillnan_first_frame(target_df.copy())



#print(evaluate(result_df,ext_labels))    

    
    