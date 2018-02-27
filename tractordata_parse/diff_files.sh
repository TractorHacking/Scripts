#!/bin/bash

function usage()
{
  printf "Usage: %b FILE1 FILE2 [flags]" $0
  exit 1
}

if [[ $# -lt 2 ]] 
then
  usage
fi

PROGNAME=./main.py
FILE1="$1"
FILE2="$2"
shift 2

diff -u <("$PROGNAME" dump-ids "$FILE1" --diff-friendly $@) <("$PROGNAME" dump-ids "$FILE2" --diff-friendly $@)
