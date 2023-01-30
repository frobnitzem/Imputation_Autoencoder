#!/bin/bash
# Create a TODO list - one list for each GPU
# then execute a jsrun to traverse it and compute all r^2 quantities
#
# Note: this should be run from within a job-script executed
# inside batch-hm (so as to minimize the chance for OOM errors).

DIR=/gpfs/alpine/proj-shared/bif138/rogersdd/genomeai/genomeai

ls -1 | sed -n -e 's/IMPUTATOR//p' | sort -n >todo
nline=`wc -l todo | awk '{print $1}'`

done=`cat r2.?.out | grep -c 'Result ='`
# check for previously completed tile.
if [ $nline -eq $done ]; then
    exit 0
fi
for((i=1; i<=6; i++)); do
  (for line in `seq $i 6 $nline`; do
    sed -n -e ${line}p todo
  done) >todo.$i
  rm -f r2.$i.err
  jsrun -g1 -c7 -bpacked:7 -n1 -i \
	--stdio_stdout r2.$i.out --stdio_stderr r2.$i.err \
	python3 $DIR/compute_r2.py ../config.yaml tile.yaml `cat todo.$i` 
done
#jslist
jswait all
