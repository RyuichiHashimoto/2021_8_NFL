import matplotlib.pyplot as plt


def get_fig_axes(nRow:int,nCol:int, figsize = (15,10)):
    assert nRow > 0 and nCol > 0
    assert len(figsize) == 2 and figsize[0] > 0 and figsize[1] > 0

    return plt.subplots(nRow,nCol,figsize = figsize);
