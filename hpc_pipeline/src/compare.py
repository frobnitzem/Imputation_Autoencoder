""" Manually run steps to inspect autoencoder models
    saved inside IMPUTATOR folders.
"""
import pandas as pd

a = pd.read_csv("chr22_old/22_33655304-33899020/22_33655304-33899020_summary.csv")
b = pd.read_csv("chr22_new/22_33655304-33899020/summary.csv")

print(a['value'].mean(), a['value'].max())
print(b['value'].mean(), b['value'].max())

# bits from /ccs/proj/bif138/rogersdd/imputator_package/genomeai/inference_function_dip_oh.py
import torch
#import torch.nn.functional as F
from genomeai.autoencoder import Autoencoder
from genomeai.configs import read_tile
from genomeai.hyper import HyperParam, read_param_py # for pytorch models

tile = read_tile("chr22_new/22_33655304-33899020/tile.yaml")
# see pydantic docs
params = HyperParam.fromfile("chr22_new/22_33655304-33899020/IMPUTATOR0/params.json")
loaded_model = Autoencoder(input_dim=tile.nvar*4,
                           output_dim=tile.nvar*4,
                           params=params, devices='cpu')
loaded_model.load_state_dict(torch.load(meta_path, map_location=torch.device('cpu')))
# checking existing functions, running for sanity checks / comparisons
loaded_model.get_r2()
# do_epoch()
# pre-requisite: store one set of parameter values and load into
#   both models, separately.  Then run steps on each model and compare
# Need: can't use leaky_relu function, must check normalization on loss function
# compare loss function computation to pytorch loss function
# check progress counters vs. time

todo = "chr22_old/22_23152772-23221729"
