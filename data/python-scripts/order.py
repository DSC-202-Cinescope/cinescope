#!/usr/bin/python3

import json

# Load JSON
with open("persons_ordered.json", "r", encoding="utf-8") as file:
        data = [json.loads(line) for line in file]

# Sort the data by 'id'
sorted_data = sorted(data, key=lambda x: x['id'])

# Write the sorted data
with open("sorted-data.json", "w", encoding="utf-8") as file:
    for entry in sorted_data:
        file.write(json.dumps(entry) + "\n")

print("Sorted data has been saved")
