#!/bin/bash

# Change directory to the 'data' folder
cd data

# Loop through each CSV file in the folder
for filename in *.csv; do

  # Save the header row to a temporary file
  head -n1 "$filename" > header.tmp

  # Sort the remaining lines in the file based on the first field, ignoring the header
  tail -n+2 "$filename" | sort -t',' -k1 -o "$filename.tmp"

  # Re-attach the header row to the sorted data
  cat header.tmp "$filename.tmp" > "$filename"

  # Remove the temporary files
  rm header.tmp "$filename.tmp"

done