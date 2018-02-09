#!/bin/bash

for fullfile in data/*.csv; do
	name=${fullfile##*/}
	file=${name%.csv}
	mkdir filedata/"$file"
	./main.py $fullfile --collate > filedata/"$file"/"$file""_collate.txt"
	./main.py $fullfile --dump-ids > filedata/"$file"/"$file""_dumpids.txt"
done
