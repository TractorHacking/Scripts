#!/bin/bash

src=$1
dest=$2

for file in "$src"/*.csv; do
	echo $file
	python tabulate.py "$file" "$dest"
done
