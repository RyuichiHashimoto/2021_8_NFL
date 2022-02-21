import numpy as np
import pandas as pd

def convert_3d_to_2d(points, from_point:np.array,to_point:np.array):
    """
    3次元空間を２次元空間へ投影させる。
    

    args:
        points: 3次元空間内の点（x,y,z）
        from_point: 視点（どこから見るか）
        to_point: 視心（どこを視るか）

    Returns:
        pd.DataFrame
        
        列ラベル
            奥行き: depth
            水平: horizon
            垂直: vertical        
        個数：pointsのレコード数と等しい        
    """

    a = np.linalg.norm(to_point[:2]-from_point[:2],ord=2)
    b = np.linalg.norm(to_point-from_point,ord=2)
    
    if(a<1e-6):
        sin_theta = 0
        cos_theta = 1
    else:
        tmp_a = (to_point - from_point)/a
        sin_theta = tmp_a[1]
        cos_theta = tmp_a[0];
                    
    if (b<1e-6):
        sin_phi = 0;                
        cos_phi = 1;                
    else:
        tmp_b = (to_point - from_point)/b
        sin_phi = tmp_b[2];        
        cos_phi = a/b
    

    
    rotmat = [
        [cos_phi*cos_theta, cos_phi*sin_theta, sin_phi],
        [-1*sin_theta, cos_theta,0],
        [-1*sin_phi*cos_theta, -sin_phi*sin_theta, cos_phi]
    ]
                    
    #x_mat = generate_rotation_maxrix(angle = 180,axis="x",isDeg=True);
    #y_mat = generate_rotation_maxrix(angle = 180,axis="y",isDeg=True);
    #z_mat = generate_rotation_maxrix(angle = 180,axis="z",isDeg=True);

    ret_df = (rotmat@(points-from_point).T).T

    

    

    

    
    ret_df = ret_df.rename(columns = {0:"depth",1:"horizon",2:"vertical"})
    ret_df["horizon"] = ret_df["horizon"]*-1
    
    
    return ret_df;



"""
def convert_3d_to_2d(points, from_point:np.array,to_point:np.array):

    3次元空間を２次元空間へ投影させる。
    

    args:
        points: 3次元空間内の点（x,y,z）
        from_point: 視点（どこから見るか）
        to_point: 視心（どこを視るか）

    Returns:
        pd.DataFrame
        
        列ラベル
            奥行き: depth
            水平: horizon
            垂直: vertical        
        個数：pointsのレコード数と等しい        
     
    a = np.linalg.norm(to_point[:2]-from_point[:2],ord=2)
    b = np.linalg.norm(to_point-from_point,ord=2)
    
    if(a<1e-6):
        sin_theta = 0
        cos_theta = 1
    else:
        tmp_a = (to_point - from_point)/a
        sin_theta = tmp_a[1]
        cos_theta = tmp_a[0];
                    
    if (b<1e-6):
        sin_phi = 0;                
        cos_phi = 1;                
    else:
        tmp_b = (to_point - from_point)/b
        sin_phi = tmp_b[2];        
        cos_phi = a/b
    
        
    
    
    rotmat = [
        [cos_phi*cos_theta, cos_phi*sin_theta, sin_phi],
        [-1*sin_theta, cos_theta,0],
        [-1*sin_phi*cos_theta, -sin_phi*sin_theta, cos_phi]
    ]
                    
    
    ret_df = (rotmat@(points-from_point).T).T
    ret_df = ret_df.rename(columns = {0:"depth",1:"horizon",2:"vertical"})
    
    
    return ret_df;
"""


def generate_rotation_maxrix(angle:np.float64,axis,isDeg=True):
    """３次元空間において、指定下軸周りに回転する行列の生成/

    args:
        _angle: 角度( 弧度法(Deg)　or ラジアン)
        isDeg: 弧度法かどうか
        axis: 回転軸

    Returns:
        axisで指定した軸まわりに角度_angleの回転を行う行列
    
    Tips:
        弧度法: (-180 <= _angle <= 180)
        ラジアン: ( -pi <= _angle <= pi)
    """
    
    
    if (isDeg):
        ang = np.deg2rad(angle);
    else:
        ang = angle


    cos = np.cos(ang);
    sin = np.sin(ang);
    
    if (axis == "x"):
        rotmat = [
            [1, 0,      0],
            [0, cos,    -1*sin],
            [0, sin,    cos]
        ]   
    elif(axis == "y"):
        rotmat = [
        [cos,       0,  sin],
        [0,         1,  0  ],
        [-1*sin,    0, cos ]
    ]
    elif (axis=="z"):
        rotmat = [
            [cos,   -1*sin, 0],
            [sin,   cos,    0],
            [0,     0,      1]
        ]
    else:
        raise Exception(f"unknown axis is specified {axis}")
    
    return np.array(rotmat);



"""
def generate_xz_rotation_maxrix(_angle:np.float64,isDeg=True):
    ３次元空間において、y軸周りに回転する行列の生成/

    args:
        _angle: 角度( 弧度法(Deg)　or ラジアン)
        isDeg: 弧度法かどうか

    Returns:
        y軸わまりに角度_angleの回転を行う行列
    
    Tips:
        弧度法: (-180 <= _angle <= 180)
        ラジアン: ( -pi <= _angle <= pi)
    
    
    
    if (isDeg):
        angle = np.deg2rad(_angle);

    cos = np.cos(angle);
    sin = np.sin(angle)
    
    rotmat = [
        [cos,0,sin],
        [0,1,0],
        [-1*sin,0,cos]
    ]
    return np.array(rotmat);

def generate_yz_rotation_maxrix(_angle:np.float64,isDeg=True):
    ３次元空間において、x軸周りに回転する行列の生成/

    args:
        _angle: 角度( 弧度法(Deg)　or ラジアン)
        isDeg: 弧度法かどうか

    Returns:
        y軸わまりに角度_angleの回転を行う行列
    
    Tips:
        弧度法: (-180 <= _angle <= 180)
        ラジアン: ( -pi <= _angle <= pi)
    
    
    
    if (isDeg):
        angle = np.deg2rad(_angle);

    cos = np.cos(angle);
    sin = np.sin(angle)
    
    rotmat = [
        [1,0,0],
        [0,cos,-1*sin],
        [0,sin,cos]
    ]
    return np.array(rotmat);
"""

