from pathlib import Path
import csv

csvs = sorted(Path("data").glob('*.csv'))
current_file_number = 0
written_headers = True
current_file = None

for csv in csvs:
    file_number = int(csv.stem)

    if file_number % 10 == 0:
        if current_file:
            current_file.close()

        current_file_number += 1
        written_headers = False
        current_file = open(f"data/{current_file_number:08}.csv", "a")

    with open(csv, 'r') as f:
        for ln, line in enumerate(f):
            if ln == 0 and not written_headers:
                current_file.write(line)
                written_headers = True
                continue
            elif ln != 0:
                current_file.write(line)

