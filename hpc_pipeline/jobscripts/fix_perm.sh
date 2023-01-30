#!/bin/bash
# Submitted from dtn, change file permissions in case umask was not 007
#SBATCH -J chmod
#SBATCH -t 120
#SBATCH -A stf006
#SBATCH -N 1

for dir in chr[4-9] chr1[0-6]; do
    find $dir -user $USER -type d -print0 | xargs -0 chmod 770
    find $dir -user $USER -type f -print0 | xargs -0 chmod 640
done
