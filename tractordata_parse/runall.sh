#!/bin/bash

for fullfile in data/*.csv; do
	name=${fullfile##*/}
	file=${name%.csv}
	mkdir filedata/"$file"
	./main.py --collate > filedata/"$file"/"$file""_collate.txt"
	./main.py --dump-ids > filedata/"$file"/"$file""_dumpids.txt"
done
