#!/usr/bin/env python3
# Run through the output of a tile and summarize
# its relative success by outputting the following numbers:
#
# - error code(s) from logfile
# - #models mentioned in logfile (containing Mean: line)
# - #models saved (based on IMPUTATOR*)
# - #models in summary.csv (containing r2 value), 0 if missing
# - best r^2 (log file), -1 if missing
# - best r^2 (summary.csv), -1 if missing
# - processing time from log
#
# Note: extra functionality to parse recomputed r2 logs
# and store training history / find best models from the log-file.

from typing import Dict

from pathlib import Path
import json
import re

import pandas as pd

# Parse out lines like:
"""Model: 39 num_gpu: 1 Epoch 100 Mean R-squared per variant for each val input [0.15863364430894308, 0.22784697357723574, 0.30983866056910575] Mean: 0.2321064261517615"""
mean_re = re.compile(r'Model: ([0-9]*) .* Epoch ([0-9]*) .* Mean: (0\.[0-9]*)')
complete_re = re.compile(r'Completed in ([0-9]*) seconds')

"""
Error codes:
     1 EmptyDataError - bad VCF input, usually by data.py:82 (load_data)
     2 'my_GT = callset['calldata/GT']' - with callset=None, bad VCF input
     4 Out of Memory Error
     8 AssertionError - multiple reasons for this
"""

def parse_r2(fname):
    """ Parse lines of the form::

        Model = 18
        State = TrialState.COMPLETE
        Result = 0.20672794339622644

    to extract a dictionary of {model: result} for all COMPLETE trials.
    """
    ans = {}
    state = 0 # parser state
    with open(fname, encoding='utf-8') as f:
        for line in f:
            if line.startswith('Model = '):
                state = 1
                model = int(line.split()[-1])
            elif state == 1:
                assert line.startswith('State = ')
                if 'COMPLETE' not in line:
                    state = 0
                else:
                    state = 2
            elif state == 2:
                assert line.startswith('Result = ')
                result = float(line.split()[-1])
                ans[model] = result
                state = 0
    return ans

def reconstruct_summary(pre):
    # read all r2.log files
    ans = {}
    for r2name in pre.glob('r2.*out'):
        ans.update(parse_r2(r2name))
    assert len(ans) > 0, "No r2 logs read."
    
    # read existing summary.csv (if present)
    summary = pre/'summary.csv'
    summary2 = pre/'summary_r2.csv'
    if summary.exists():
        df = pd.read_csv(summary, index_col=0)
        cols = df.columns
        data = []
        for _, row in df.iterrows():
            data.append( [row[c] for c in cols] )
        lookup = dict((d[0],i) for i,d in enumerate(data))
    else:
        cols = "number,value,params_L1,params_L2,params_activation,params_batch_size,params_beta,params_decay_rate,params_disable_alpha,params_flip_alpha,params_gamma,params_inverse_alpha,params_learn_rate,params_loss_type,params_n_layers,params_optimizer_type,params_rho,params_size_ratio,state".split(',')
        data = []
        lookup = {}
    rename = {'learn_rate': 'learning_rate'}
    def param_name(k): # lookup the parameter name from the corresponding col.
        name = k.split('_',1) # chop params_
        assert name[0] == 'params', k
        name = name[1]
        if name in rename:
            name = rename[name]
        return name
    # augment all r2 values with parameters
    for model, r2 in ans.items():
        par = json.load( open(pre / f"IMPUTATOR{model}/params.json") )
        if model in lookup:
            v = lookup[model]
        else:
            data.append( [] )
            v = len(data)-1
        data[v] = [model, r2] + [par.get(param_name(k), None) for k in cols[2:-1]] + ['COMPLETE']

    pd.DataFrame(data, columns=cols).to_csv(summary2)

class ModelInfo:
    """ Stores the training history for a given model number.
    """
    def __init__(self, num, epoch=None, mean=None):
        self.number = num
        assert not ((epoch is None) ^ (mean is None)), \
                    "Epoch and mean must both be present or absent together."
        if epoch is None:
            self.epochs = []
        else:
            self.epochs = [epoch]
        self.mean = [mean]
    def update(self, epoch, mean):
        self.epochs.append(epoch)
        self.mean.append(mean)
    def exists(self, pre):
        b = self.number
        sz = (pre / f"IMPUTATOR{b}/thinc.bin").stat().st_size
        if sz < 1024*1024:
            print(f"Model {b} has only size: {sz/1024} kB")
            return False
        try:
            u = json.load( open(pre / f"IMPUTATOR{b}/params.json") )
        except:
            print(f"Unable to load params.json for model {b}")
            return False
        return True

def parse_log(f):
    err = 0
    time = None
    models : Dict[int, ModelInfo] = {}
    for line in f:
        m = mean_re.match(line)
        if m is not None:
            num = int(m[1])
            epoch = int(m[2])
            mean = float(m[3])
            if num in models:
                models[num].update(epoch, mean)
            else:
                models[num] = ModelInfo(num, epoch, mean)
            continue
        m = complete_re.match(line)
        if m is not None:
            time = int(m[1])
            break
        if "EmptyDataError:" in line:
            err |= 1
            continue
        if "my_GT = callset['calldata/GT']" in line:
            err |= 2
            continue
        if "OutOfMemoryError" in line \
            or "consumes too much memory" in line:
            err |= 4
            continue
        if "AssertionError" in line:
            err |= 8
            continue
    return err, time, models

def check(pre, nchr):
    with open(pre/'hyperparam.log', encoding='utf-8') as f:
        err, time, models = parse_log(f)
    model1 = len( models )
    model2 = len( [d for d in pre.glob('IMPUTATOR[0-9]*')] )
    sum_file = pre/'summary.csv'
    best_log = max((m.mean[-1] for _,m in models.items()), default=-1.0)
    if sum_file.exists():
        df = pd.read_csv(sum_file, index_col=0)
        #model3 = len(df.groupby('number')) # would count all models
        # count every row with a value
        model3 = len( df.dropna(subset='value') )
        best_sum = df['value'].max()
    else:
        model3 = 0
        best_sum = -1.0
    return err, model1, model2, model3, best_log, best_sum, time or -1

def list_best(pre, nchr):
    with open(pre/'hyperparam.log', encoding='utf-8') as f:
        err, time, models = parse_log(f)
    mtop = [(m.mean[-1], num) for num,m in models.items()]
    mtop.sort(reverse=True)
    i = 0
    while i < 10:
        if len(mtop) <= i:
            break
        m = models[mtop[i][1]]
        if not m.exists(pre):
            mtop.pop(i)
            continue

        print(mtop[i][1], mtop[i][0])
        i += 1
    return None

# e.g. '1_12266938-12604081'
# scans directory 'chr1/1_12266938-12604081'
def main(argv):
    best = False
    r2 = False
    while len(argv) > 1:
        if argv[1] == "-b":
            del argv[1]
            best = True
        elif argv[1] == "-r":
            del argv[1]
            r2 = True
        else:
            break
    assert len(argv) > 1, f"Usage: {argv[0]} <dir> ..."

    for tile in argv[1:]:
        nchr = 'chr' + tile.split('_', 1)[0]
        pre = Path(nchr) / tile
        if best:
            list_best(pre, nchr)
        if r2:
            reconstruct_summary(pre)
        if not (best or r2):
            ans = check(pre, nchr)
            print(f"{tile} {' '.join(map(str,ans))}")

if __name__=="__main__":
    import sys
    main(sys.argv)
