#!/usr/bin/python3

import requests
import time
import json
import os

API_KEY = '4973673a165a242136f2725ae4d307e5'
URL = 'https://api.themoviedb.org/3/person/'
OUTPUT_FILE = 'actor_credits.json'

def get_last_id():
    if not os.path.exists(OUTPUT_FILE):
        return None
    with open(OUTPUT_FILE, 'r') as file:
        last_id = None
        for line in file:
            try:
                actor_data = json.loads(line.strip())
                actor_id = movie_data.get('id')
                if actor_id:
                    last_id = actor_id
            except json.JSONDecodeError:
                continue
        return last_id

def get_actor_movie_ids(actor_id):
    url = f"{URL}{actor_id}/movie_credits"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        movie_ids = [movie['id'] for movie in data.get('cast', [])]
        return {
            "actor_id": actor_id,
            "movie_ids": movie_ids
        }
    else:
        print(f"Failed to fetch actor ID {actor_id}. Status code: {response.status_code}")
        return None

def write_to_json(actor_data):
    simplified_data: {
        "actor_id": data["actor_id"],
        "movie_ids": data["movie_ids"]
    }
    with open(OUTPUT_FILE, 'a') as file:
        json.dump(simplified_data, file, indent=4)
        file.write("\n")
    print(f"Data written to {OUTPUT_FILE}")

def main():
    last_id = get_last_id()
    print("Last written actor Id: {last_id}")

    response = requests.get(f"{URL}latest", params={'api_key': API_KEY})
    if response.status_code == 200:
        latest_actor = response.json().get('id')
        
        start_id = (last_id + 1) if last_id else 1

        for actor_id in range(start_id, latest_actor + 1):
            actor_data = get_actor_movie_ids(actor_id)
            if actor_data:
                write_to_json(actor_data)
                print(f"Actor stored: {actor_id}")
    else:
        print(f"Failed to fetch latest movie. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
