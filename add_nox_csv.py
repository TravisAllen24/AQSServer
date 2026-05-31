INPUT_FILE = "data_log.csv"

OLD_HEADER = "timestamp,temp (C),humidity (%),dew point (C),co2 (ppm),voc_raw,voc_index,pm10 (ug/m3),pm25 (ug/m3),pm100 (ug/m3)"
NEW_HEADER = "timestamp,temp (C),humidity (%),dew point (C),co2 (ppm),voc_raw,voc_index,nox_raw,nox_index,pm10 (ug/m3),pm25 (ug/m3),pm100 (ug/m3)"

# nox_raw and nox_index are inserted after voc_index (index 6), before pm10 (index 7)
INSERT_AFTER = 6

with open(INPUT_FILE, "r", newline="") as f:
    lines = f.readlines()

if not lines:
    raise SystemExit("File is empty.")

header = lines[0].rstrip("\n")
if header != OLD_HEADER:
    print(f"Warning: header doesn't match expected.\nFound:    {header}\nExpected: {OLD_HEADER}")

output_lines = [NEW_HEADER + "\n"]

for line in lines[1:]:
    stripped = line.rstrip("\n")
    if not stripped:
        output_lines.append("\n")
        continue
    cols = stripped.split(",")
    cols.insert(INSERT_AFTER + 1, "-")
    cols.insert(INSERT_AFTER + 1, "-")
    output_lines.append(",".join(cols) + "\n")

with open(INPUT_FILE, "w", newline="") as f:
    f.writelines(output_lines)

print(f"Done. Processed {len(output_lines) - 1} data rows.")