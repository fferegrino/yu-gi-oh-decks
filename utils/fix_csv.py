"""
This code processes all CSV files in the 'data' folder by calling the remove_newlines function for each file.
The remove_newlines function reads in each CSV file, removes new lines from the 'deck_description' and
'deck_excerpt' columns, and writes the modified data back to the same file.
"""

import csv
import glob
import tempfile
import shutil

def remove_newlines(input_file):
    with open(input_file, 'r') as infile, \
         tempfile.NamedTemporaryFile(mode='w', delete=False) as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

        # Write the header row to the output file
        writer.writeheader()

        for row in reader:
            row['deck_description'] = row['deck_description'].replace('\n', ' ')
            if row['deck_excerpt']:
                row['deck_excerpt'] = row['deck_excerpt'].replace('\n', ' ')

            writer.writerow(row)

    shutil.move(outfile.name, input_file)

for filename in glob.glob('data/*.csv'):
    remove_newlines(filename)