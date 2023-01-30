#!/usr/bin/env python3
#
# List out the top 10 models present in the `summary.csv` file
# and check that their output json and parameter values (thinc.bin)
# are good.
# If everything checks out, create "best.txt" and "worst.txt"
# files.  All model parameters in "worst.txt" are suitable for deletion.
#
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

    best = df2.iloc[:10]['number'].values
    for b in best:
        sz = (pre / f"IMPUTATOR{b}/thinc.bin").stat().st_size
        if sz < 1024*1024:
            print(f"Model {b} has only size: {sz/1024} kB")
            return
        try:
            u = json.load( open(pre / f"IMPUTATOR{b}/params.json") )
        except:
            print(f"Unable to load params.json for model {b}")
            return


    with open(pre / 'best.txt', 'w') as f:
        f.write("\n".join(map(str, df2.iloc[:10]['number'])) + '\n')

    with open(pre / 'worst.txt', 'w') as f:
        f.write("\n".join(map(str, df2.iloc[10:]['number'])) + '\n')

# e.g. 'chr1/1_12266938-12604081'
def main(argv):
    assert len(argv) > 1, f"Usage: {argv[0]} <dir> ..."
    for dirname in argv[1:]:
        mark( Path(dirname) )

if __name__=="__main__":
    import sys
    main(sys.argv)
