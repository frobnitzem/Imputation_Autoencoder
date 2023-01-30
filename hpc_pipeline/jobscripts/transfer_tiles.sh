#!/bin/bash
# Submitted from dtn - unused template for lots of parallelism in file copy
#SBATCH -J transfer_tiles
#SBATCH -o %x.%j
#SBATCH -t 24:00:00
#SBATCH -A bif138
#SBATCH -N 1
#SBATCH -d singleton
#
# each dtn node has 16 processors
# use gnu parallel to launch a transfer function over every tile
#
# The "-d singleton" line ensures that only one of these
# scripts will run at a time.

function transfer_tile {
    # $1 is the tile directory
    # send successes to `transfer_ok.log`
    # and failure messages to `transfer_fail.log`
    if ! [ -s $1/best.txt ]; then
        echo "$1 No best.xyz" >>transfer_fail.log
        return
    fi

    # Note our success so the tile isn't transferred again.
    echo "$1" >>transfer_ok.log
}

export -f transfer_tile

for dir in chr[1-9] chr1[0-9] chr2[0-2]; do
    echo $dir
    cd $dir
    # Run transfer_tile function over all tiles listed in tiles.done,
    # but not in transfer_ok.log
    touch transfer_ok.log
    parallel transfer_tile ::: $(comm -23 <(sort -u tiles.done) <(sort -u transfer_ok.log) )
    cd ..
    break
done
