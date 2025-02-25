#!/usr/bin/python3

import requests
import json
import os
import time

API_KEY = '4973673a165a242136f2725ae4d307e5'
URL = 'https://api.themoviedb.org/3/person/'
OUTPUT_FILE = 'actor_movie_ids.json'

# Get the last saved actor ID from the output file
def get_last_saved_actor_id():
    if not os.path.exists(OUTPUT_FILE):
        return None  # No previous data exists
    with open(OUTPUT_FILE, 'r') as file:
        last_id = None
        for line in file:
            try:
                actor_data = json.loads(line.strip())
                actor_id = actor_data.get('actor_id')
                if actor_id:
                    last_id = actor_id
            except json.JSONDecodeError:
                continue  # Skip any corrupted lines
        return last_id

# Get the latest actor ID from TMDB
def get_latest_actor_id():
    url = f"{URL}latest"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        print(f"Failed to fetch the latest actor ID. Status code: {response.status_code}")
        return None

# Fetch movie credits for an actor
def get_actor_movie_ids(actor_id):
    url = f"{URL}{actor_id}/movie_credits"
    params = {'api_key': API_KEY}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            movie_ids = [movie['id'] for movie in data.get('cast', [])]
            return movie_ids
        else:
            print(f"Skipping actor ID {actor_id}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error for actor ID {actor_id}: {e}")
        return None

# Append movie data to output file
def append_to_json_file(actor_id, movie_ids):
    data = {"actor_id": actor_id, "movie_ids": movie_ids}
    with open(OUTPUT_FILE, 'a') as file:
        file.write(json.dumps(data) + '\n')

# Main function
def main():
    last_saved_actor_id = get_last_saved_actor_id()
    latest_actor_id = get_latest_actor_id()

    if not latest_actor_id:
        print("Could not fetch the latest actor ID. Exiting.")
        return

    # Determine starting point
    start_actor_id = last_saved_actor_id + 1 if last_saved_actor_id else 1

    for actor_id in range(start_actor_id, latest_actor_id + 1):
        movie_ids = get_actor_movie_ids(actor_id)
        if movie_ids is not None:
            append_to_json_file(actor_id, movie_ids)
            print(f"Processed and saved actor ID {actor_id}")
        else:
            print(f"Skipped actor ID {actor_id} due to missing data.")

if __name__ == "__main__":
    main()
