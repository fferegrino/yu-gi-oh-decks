#!/bin/bash

# change directory to the data folder
cd data

# loop through all files in the folder
for file in *
do
  # sort the lines of the file and overwrite the original file
  sort "$file" -o "$file"
done
