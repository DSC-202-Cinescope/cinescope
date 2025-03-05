#!/usr/bin/python3

import pandas as pd
import json
import ast
import csv
import sys
import os

tmdb_json = sys.argv[1]

print("Input file: ", tmdb_json)

data = []
with open(tmdb_json, 'r', encoding='utf-8') as file:

    for line in file:
        try:
            data.append(json.loads(line.strip()))
        except json.JSONDecodeError as e:
            print(f"Error parsing line: {line.strip()} - {e}")

tmdb = os.path.splitext(tmdb_json)[0]
print(f"File prefix: {tmdb}")

tmdb_csv = tmdb + ".csv"
print(f"Converting json file to: {tmdb_csv}")

with open(tmdb_csv, 'w', newline='', encoding='utf-8') as csvfile:
    if isinstance(data, list):
        writer = csv.DictWriter(csvfile, fieldnames=(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    elif isinstance(data, dict):
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

# JSONB objects need to be properly formatted
df = pd.read_csv(tmdb_csv)

#df["belongs_to_collection"] = df["belongs_to_collection"].apply(lambda x: json.dumps(ast.literal_eval(x)) if pd.notna(x) else x)
#df["production_companies"] = df["production_companies"].apply(lambda x: json.dumps(ast.literal_eval(x)) if pd.notna(x) else x)
#df["production_countries"] = df["production_countries"].apply(lambda x: json.dumps(ast.literal_eval(x)) if pd.notna(x) else x)
#df["spoken_languages"] = df["spoken_languages"].apply(lambda x: json.dumps(ast.literal_eval(x)) if pd.notna(x) else x)

df = df.drop_duplicates(subset="actor_id", keep="first")
df = df.applymap(lambda x: " ".join(str(x).splitlines()) if pd.notna(x) else x)

df.to_csv(tmdb_csv, index=False)

