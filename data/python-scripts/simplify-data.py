import json
import sys
import csv

# Load the JSON file
input_filename = sys.argv[1]
#json_output_filename = "actor-movies-id-master.json"
csv_output_filename = "actor-movie-ids-45-50.csv"

flattened_data = set()

# Read and parse JSON line by line
with open(input_filename, "r", encoding="utf-8") as file:
    for line in file:
        try:
            data = json.loads(line.strip())  # Load each line as JSON
            for movie in data.get("movie_ids", []):
                flattened_data.add((data["actor_id"], movie["id"]))
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON line: {e}")

unique_data = [{"actor_id": actor_id, "movie_id": movie_id} for actor_id, movie_id in flattened_data]

# Save the cleaned JSON list
#with open(json_output_filename, "w", encoding="utf-8") as file:
#    json.dump(unique_data, file, indent=4)

# Save the flattened data as CSV
with open(csv_output_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["actor_id", "movie_id"])
    writer.writeheader()  # Write the header
    writer.writerows(unique_data)  # Write the data

print(f"Flattened data saved to {csv_output_filename}")
