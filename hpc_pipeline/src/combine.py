""" Combine results from all "summary.csv" files in the named
    tile-directories.  The output will have extra columns
    for chr,start,end
"""
import pandas as pd
from pathlib import Path

cols = "number,value,params_L1,params_L2,params_activation,params_batch_size,params_beta,params_decay_rate,params_disable_alpha,params_flip_alpha,params_gamma,params_inverse_alpha,params_learn_rate,params_loss_type,params_n_layers,params_optimizer_type,params_rho,params_size_ratio,state".split(',')

def str2int(x):
    return None if len(x) == 0 else int(x)

def load_csv(tile):
    pre, post = tile.split('_', 1)
    start, end = post.split('-')
    start = str2int(start)
    end = str2int(end)

    chr_id = int(pre)
    if pre == '22':
        pre = '22_new'
    pre = Path("chr" + pre)

    try:
        #df = pd.read_csv(pre / tile / "summary.csv")
        df = pd.read_csv(Path(tile) / "summary.csv")
    except FileNotFoundError:
        print(f"{tile} - no summary.csv")
        return []
    df.dropna(subset=['value'], inplace=True)
    df = df[cols]
    df['chr'] = chr_id
    df['start'] = start
    df['end'] = end
    return [df]

def main(argv):
    assert len(argv) >= 3, f"Usage: {argv[0]} <out.csv> <tile1> ..."
    out = Path(argv[1])
    lst = []
    if out.exists():
        lst.append(pd.read_csv(out))
    for tile in argv[2:]:
        lst.extend(load_csv(tile))

    df = pd.concat(lst)
    df.to_csv(out)

if __name__=="__main__":
    import sys
    main(sys.argv)
