import pickle
import os
import pandas as pd
import json


def load_json(filepath):
    if (not os.path.exists(filepath)):
        raise Exception(f"The file {filepath} was not found")

    if (not filepath.endswith(".json")):
        raise Exception("The file is ." +filepath.split(".")[-1] + "file, not json (.json) file");

    
    return json.load(open(filepath,"r"));




def save_as_pickle(data,filePath,overwrite = False):
    os.makedirs("/".join(filePath.replace("\\","/").split("/")[:-1]),exist_ok=True)
    
    if( (not overwrite ) and (os.path.exists(filePath))):
        raise Exception("The file already exists\n" + filePath)
    else:
        pickle.dump( data,open(filePath,"wb"));

def load_pickle(file_path):


    if ( not os.path.exists(file_path)):
        raise Exception("There is no such a file");

    if (not file_path.endswith(".pkl")):
        raise Exception("The file is ." +file_path.split(".")[-1] + "file, not pickle (.pkl) file");
    
    
    return pickle.load(open(file_path,"rb"));


def save_as_csv(data,filePath,overwrite = False):
    os.makedirs("/".join(filePath.replace("\\","/").split("/")[:-1]),exist_ok=True)
    
    
    if (not filePath.endswith(".csv")):
        raise Exception("The file is "+  filePath.split(".")[-1]+ ", not csv file");
    
    if( (not overwrite ) and (os.path.exists(filePath))):
        raise Exception("The file already exists\n" + filePath)
    
        
    if ( isinstance(data,pd.core.frame.DataFrame)):
        data.to_csv(filePath,index=False);
    else:
        raise Exception(f"cannot save as csv format because of data type {type(data)}");


def save_data_as_csv_and_pkl(data,filePath,overwrite = False):
    
    """
        自作したデータをpklファイルとcsvファイルで保存するスクリプト

     args:
        data: ファイル出力するデータ
        filePath: ファイル名（絶対パス推奨。最後は必ずピリオドで終了すること）
        ovewwrite: 上書きするか (True: すでにファイルがあっても保存。Falseなら、すでにファイルがあれば例外)
                    
    Returns:
        None
    
    Exception:
        filepathの後ろがピリオドで終わらない場合
    """

    if (not filePath.endswith(".")):
        raise Exception("filePath must be end with .");

    
    save_as_pickle(data,filePath+"pkl",overwrite)
    save_as_csv(data,filePath+"csv",overwrite)