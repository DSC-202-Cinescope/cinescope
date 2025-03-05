#!/usr/bin/python3

import requests
import time
import json
import os

API_KEY = '4973673a165a242136f2725ae4d307e5'
URL = 'https://api.themoviedb.org/3/movie/'
OUTPUT_FILE = 'movies.json'

def get_last_id():
    if not os.path.exists(OUTPUT_FILE):
        return None
    with open(OUTPUT_FILE, 'r') as file:
        last_id = None
        for line in file:
            try:
                movie_data = json.loads(line.strip())
                movie_id = movie_data.get('id')
                if movie_id:
                    last_id = movie_id
            except json.JSONDecodeError:
                continue
        return last_id

def get_movies(movie_id):
    url = f"{URL}{movie_id}"
    params = {'api_key': API_KEY}
    response = requests.get(url, params=params) 
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch movie ID {movie_id}. Status code: {response.status_code}")
        return None

def write_to_json(movie_data):
  with open(OUTPUT_FILE, 'a') as file:
      json.dump(movie_data, file)
      file.write("\n")

def main():
    last_id = get_last_id()
    print("Last writte movie Id: {last_id}")

    response = requests.get(f"{URL}latest", params={'api_key': API_KEY})
    if response.status_code == 200:
        latest_movie = response.json().get('id')
        
        start_id = (last_id + 1) if last_id else 1

        for movie_id in range(start_id, latest_id + 1):
            movie_data = get_movies(movie_id)
            if movie_data:
                write_to_json(movie_data)
                print(f"Movie stored: {movie_id}")
    else:
        print(f"Failed to fetch latest movie. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
