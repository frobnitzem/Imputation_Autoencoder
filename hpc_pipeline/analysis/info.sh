#!/bin/bash
# Create tiles.nvar, showing number of variables per tile.

rm -f tiles.nvar
touch tiles.nvar

for i in [0-9]*_[0-9]*; do
    nvar=$(sed -n -e 's/.*nvar: *//p' $i/tile.yaml)
    echo "$i $nvar" >>tiles.nvar
done
