#!/usr/bin/env python3
"""
Exclude listed targets from the yaml list.
"""

import yaml

def main(argv):
    assert len(argv) >= 3, f"Usage: {argv[0]} <out.yaml> <target1> ..."
    out = argv[1]
    with open(out) as f:
        tgts = yaml.safe_load(f)

    deleted = 0
    for s in argv[2:]:
        # if this is a full directory name, shorten to the target name
        if '/' in s:
            s = s.split('/', 1)[1]
        if '-' in s:
            s = s.rsplit('-', 1)[0]
        if s in tgts:
            del tgts[s]
            deleted += 1
        else:
            print(f"{s} not present")

    print(f"Removed {deleted} targets.")
    if deleted > 0:
        with open(out, 'w') as f:
            f.write( yaml.dump(tgts) )

if __name__=="__main__":
    import sys
    main(sys.argv)
