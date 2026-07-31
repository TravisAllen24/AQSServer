import csv
from pathlib import Path

file = Path("data_log.csv")

with file.open("r", newline="") as f:
    rows = list(csv.reader(f))

for row in rows:
    if len(row) >= 4:
        del row[3]  # Remove Dew Point column

with file.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Updated {file}")