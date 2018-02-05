#!/bin/bash

for foo in *.csv; do
  ./main.py "$foo" > "${foo%.csv}.txt"
done
