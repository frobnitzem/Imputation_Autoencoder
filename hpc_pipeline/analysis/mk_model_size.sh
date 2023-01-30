#!/bin/bash
# list out the size of every IMPUTATOR directory
# given chr_disk.txt exists (created by df)

echo 'kbytes chr tile model' >model_size.csv
sed -n -e '/IMPUTATOR/ s/\// /g; s/IMPUTATOR//p' chr_disk.txt \
    | tr '\t' ' ' >>model_size.csv
