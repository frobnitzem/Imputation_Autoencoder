# generate an include file for rclone
# https://rclone.org/filtering
from pathlib import Path
import json

import pandas as pd

def mark(pre):
    df  = pd.read_csv(pre / 'summary.csv', index_col=0)
    done = len(df['value'].dropna())
    if done < 10:
        print(f"pre contains only {done} complete models.")
        return

    df2 = df.sort_values(by='value', ascending=False, kind='stable')

    best = df2.iloc[:5]['number'].values
#    for b in best:
#        sz = (pre / f"IMPUTATOR{b}/thinc.bin").stat().st_size
#        if sz < 1024*1024:
#            print(f"Model {b} has only size: {sz/1024} kB")
#            return
#        try:
#            u = json.load( open(pre / f"IMPUTATOR{b}/params.json") )
#        except:
#            print(f"Unable to load params.json for model {b}")
#            return


    with open(pre / 'include.txt', 'w') as f:
        for b in best:
            f.write(f"IMPUTATOR{b}/thinc.bin" + '\n')
            f.write(f"IMPUTATOR{b}/params.json" + '\n')
        

        f.write("summary.csv" + "\n")
        f.write("hyperparam.*" + "\n")
        f.write("tile.yaml" + "\n")

# e.g. 'chr1/1_12266938-12604081'
def main(argv):
    assert len(argv) > 1, f"Usage: {argv[0]} <dir> ..."
    for dirname in argv[1:]:
        mark( Path(dirname) )

if __name__=="__main__":
    import sys
    main(sys.argv)

