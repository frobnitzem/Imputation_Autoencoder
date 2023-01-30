""" Append all "in-progress" and "error" tiles
    to the top-level "targets.yaml" file in this directory.

    The resulting targets will look like:

        1_159642026:
          gpus_per_model: 1
          cpus_per_model: 7
          dirname: chr1/1_159642026-159734453
          out: [summary.csv]

        1_84121748:
          gpus_per_model: 2
          cpus_per_model: 14
          dirname: chr1/1_84121748-84467867
          out: [summary.csv]

    Using the location as the key will prevent adding
    the same tile twice.  Every target will list its
    gpus/cpus/out separately.

    TODO: run this script to list all error tiles
    from directories other than chr1, chr7, chr9, and
    chr21

  - data plan: keep top 10 models (~ 420 TB)
    - compare single model with "best r2" to minimac, impute, beagle
    - scrape training log file for r-squareds, etc.
"""

from pathlib import Path
import yaml

def get_name(s):
    return s.split('-', 1)[0]

def append_list(subdir, tgts):
    tgt = yaml.safe_load(open(subdir / "targets.yaml"))
    tgt = dict((get_name(t['dirname']), t) for _,t in tgt.items())
    nvar = dict((get_name(line.split()[0]), line.split()[1]) for line in open(subdir / "tiles.nvar"))

    todo = open(subdir / "tiles.errors").readlines()
    #todo.extend( open(subdir / "tiles.progress").readlines() )

    for tile in todo:
        if len(tile) == 0:
            continue
        name = get_name(tile)
        if name not in tgt:
            print(f"Warning: {name} not present in targets.yaml")
            if name in nvar:
                print(f"nvar = {nvar[name]}")
            continue
        # rebuild instead.
        #tgts[name] = tgt[name]
        dirname = str(subdir / tgt[name]['dirname'])
        ngpu = tgt[name].get('gpus_per_model',1)
        tgts[name] = {
          'gpus_per_model': ngpu,
          'cpus_per_model': ngpu*7,
          'dirname': dirname,
          'out': ['summary.csv']
        }

#>>> tgt['tile1']
#{'gpus_per_model': 1, 'cpus_per_model': 7, 'dirname': '1_159642026-159734453', 'out': ['summary.csv']}
#>>> tgt['tile100']
#{'gpus_per_model': 1, 'cpus_per_model': 7, 'dirname': '1_242185401-242197064', 'out': ['summary.csv']}
#>>> len(todo)
#1135
#>>> todo[-1]
#'1_99800367-100066304\n'

#>>> print(yaml.dump(tgt['tile100']))
#cpus_per_model: 7
#dirname: 1_242185401-242197064
#gpus_per_model: 1
#out: [summary.csv]

def main(argv):
    assert len(argv) >= 3, f"Usage: {argv[0]} <out.yaml> <dirname> ..."
    out = argv[1]
    try:
        tgts = yaml.safe_load(open(out))
    except FileNotFoundError:
        tgts = {}

    for s in argv[2:]:
        subdir = Path(s)
        assert subdir.is_dir(), f"Not a directory: {subdir}"
        append_list(subdir, tgts)

    with open(out, 'w') as f:
        f.write( yaml.dump(tgts) )

if __name__=="__main__":
    import sys
    main(sys.argv)
