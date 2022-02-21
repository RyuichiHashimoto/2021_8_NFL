



def jaccard(row): 
    a = set(row['answer'].lower().split()) 
    b = set(row['prediction'].lower().split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))