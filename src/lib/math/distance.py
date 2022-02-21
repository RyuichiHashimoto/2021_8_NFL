from scipy.spatial.distance import cdist
import numpy as np

def calc_dist_mat_cpu(X,Y,metric="euclidean"):
    return cdist(X,Y,metric);
    

