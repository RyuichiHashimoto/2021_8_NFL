import multiprocessing as mp
from multiprocessing import Pool
from tqdm import tqdm

def exe_multiprocess_ret_as_list(func,data,n_of_cpu=-1,plot_processbar = True):
    """
        func: 並列実行したい関数
        data: 並列実行するときの引数、
        n_of_cpu: 並列処理に使用するCPU
        plot_processbar: プロセスバーを表示させるか否か

        返り値の順番はdataの順番と対応している。
    """
    
    """
        defaultの場合、CPU個数-2にしている。
        （昔、知人がこの処理スピードについてまとめており、）CPU個数 - 2 が一番処理性能が良かったらしいため、それを踏襲している。
    """
    if(n_of_cpu == -1):
       n_of_cpu = mp.cpu_count() -2

    
    if (plot_processbar):
        with Pool(processes=n_of_cpu) as pool:
            imap = pool.imap(func,data);
            result = list(tqdm(imap,total=len(data)));

        return result
    else:
        p = mp.Pool(mp.cpu_count());
        s = p.map(func,data);
        p.close();
        return s;

        


        

    


def costom_sleep(i):
    sleep(i);
    return i;

if __name__ == "__main__":
    from time import sleep




    #s = exe_multiprocess_ret_as_list(costom_sleep, [3,3,3,3,3])
    s = exe_multiprocess_ret_as_list(costom_sleep, [10,2,3,4,5],plot_processbar=False)
    print(s);
    

















