#!/bin/bash
# Create lists of tiles in each state (done, progress, errors)

rm -f tiles.done tiles.progress tiles.errors

touch tiles.done tiles.progress tiles.errors

for i in [0-9]*_[0-9]*; do
    [ -d $i ] || continue
    if [ -s $i/summary.csv ]; then
        echo $i >>tiles.done
        continue
    fi 
    if (ls -d $i/IMPUTATOR* >/dev/null 2>&1); then
        echo $i >>tiles.progress
        continue
    fi
    echo $i >>tiles.errors
done

wc -l tiles.done tiles.progress tiles.errors
