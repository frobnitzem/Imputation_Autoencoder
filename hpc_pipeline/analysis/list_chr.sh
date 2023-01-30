#!/bin/bash
# List out the tiles present in the `sweep` targets.yaml file.

sed -n -e 's/.*\(chr[0-9]*\)\/.*/\1/p' targets.yaml | sort -u
