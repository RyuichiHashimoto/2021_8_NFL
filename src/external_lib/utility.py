from lib.noglobal import noglobal
import pandas as pd



def add_track_features(tracks, fps=59.94, snap_frame=10):
    """
    Add column features helpful for syncing with video data.
    """
    tracks = tracks.copy()
    tracks["game_play"] = (
        tracks["gameKey"].astype("str")
        + "_"
        + tracks["playID"].astype("str").str.zfill(6)
    )
    tracks["time"] = pd.to_datetime(tracks["time"])
    snap_dict = (
        tracks.query('event == "ball_snap"')
        .groupby("game_play")["time"]
        .first()
        .to_dict()
    )
    tracks["snap"] = tracks["game_play"].map(snap_dict)
    tracks["isSnap"] = tracks["snap"] == tracks["time"]
    tracks["team"] = tracks["player"].str[0].replace("H", "Home").replace("V", "Away")
    tracks["snap_offset"] = (tracks["time"] - tracks["snap"]).astype(
        "timedelta64[ms]"
    ) / 1_000
    # Estimated video frame
    tracks["est_frame"] = (
        ((tracks["snap_offset"] * fps) + snap_frame).round().astype("int")
    )
    return tracks




def merge_base_and_deepsort(base_sub,deepsort_sub, erase_duplicated = True):
    
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
    
    deepsort_sub = deepsort_sub.drop("key",axis=1)
    ret_df = ret_df.drop("key",axis=1)
    
    
    if (erase_duplicated):
        bec = [];
        for key,each_df in ret_df.groupby("video_frame"):
            each_df = each_df.sort_values("isDeepSpecuration")
            each_df = each_df[~each_df.duplicated(subset="label",keep='first')]
            bec.append(each_df)
    
        ret_df = pd.concat(bec)
    
    return ret_df;