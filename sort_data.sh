#!/bin/bash

cd data

for file in *.csv
do
  # create temporary file for sorting
  tmpfile=$(mktemp)

  # extract the header row to a separate file
  head -n 1 "$file" > header.csv

  # sort the remaining rows numerically
  tail -n +2 "$file" | sort -n > "$tmpfile"

  # concatenate the header row and sorted rows into a new file
  cat header.csv "$tmpfile" > sorted.csv

  # overwrite the original file with the sorted output
  mv sorted.csv "$file"

  # delete temporary files
  rm header.csv "$tmpfile"
done
