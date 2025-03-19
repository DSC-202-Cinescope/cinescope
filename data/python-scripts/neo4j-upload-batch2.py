import pandas as pd
import json
from tqdm import tqdm
from neo4j import GraphDatabase

# ========================
# Neo4j Connection Setup
# ========================
neo4j_uri = "bolt://neo4j:7687"  # Using service DNS in your Kubernetes cluster
neo4j_username = "neo4j"
neo4j_password = ""              # No password as configured
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

# ==========================================================
# STEP 1: Import People and Actor–Movie Relationships
# ==========================================================

# Load person_ids.csv into a dictionary for quick lookup
df_person = pd.read_csv("/home/jovyan/work/cinescope/data/csv-files/person_ids.csv", encoding="utf-8")
person_dict = {}
print("Loading person data...")

for _, row in tqdm(df_person.iterrows(), total=len(df_person), desc="Loading Persons"):
    try:
        person_id = int(row["id"])
    except Exception:
        continue
    person_dict[person_id] = {
        "name": row["name"],
        "popularity": row["popularity"],
        "adult": row["adult"]
    }
print("Loaded", len(person_dict), "persons from person_ids.csv")

# Retrieve existing person IDs from Neo4j
existing_person_ids = set()
with driver.session() as session:
    result = session.run("MATCH (p:Person) RETURN p.id AS id")
    for record in result:
        existing_person_ids.add(record["id"])
print("Already imported persons:", len(existing_person_ids))

# Retrieve existing movie IDs from Neo4j
existing_movie_ids = set()
with driver.session() as session:
    result = session.run("MATCH (m:Movie) RETURN m.id AS id")
    for record in result:
        existing_movie_ids.add(record["id"])
print("Already imported movies:", len(existing_movie_ids))

# Process actor-movie-ids-master.csv in chunks
actor_movie_csv = "/home/jovyan/work/cinescope/data/csv-files/actor-movie-ids-master.csv"  
with open(actor_movie_csv, "r", encoding="utf-8") as f:
    total_actor_movie_rows = sum(1 for _ in f) - 1
print("Total rows in actor-movie CSV:", total_actor_movie_rows)

actor_chunksize = 100
with pd.read_csv(actor_movie_csv, chunksize=actor_chunksize, encoding="utf-8") as reader:
    for df_chunk in tqdm(reader, total=(total_actor_movie_rows // actor_chunksize) + 1, desc="Importing Actor-Movie Relationships"):
        with driver.session() as session:
            for _, row in df_chunk.iterrows():
                try:
                    actor_id = int(row["actor_id"])
                    movie_id = int(row["movie_id"])
                except Exception:
                    continue  # Skip invalid rows

                # Focus only on the movie with movie_id = 1413976
                movie_list = [1258547, 1388760, 497, 1585, 1891, 47981, 274320, 304892, 363556, 377462, 447454, 450704, 468083, 510676, 576712, 578300, 634237, 651336, 664280, 754602, 754604, 756827, 1013120, 1014334, 1016108, 1022256, 1221352]

                if movie_id not in movie_list :
                    continue

                # Merge the Person node if not already present
                if actor_id not in existing_person_ids:
                    person_info = person_dict.get(actor_id, None)
                    if person_info:
                        session.run(
                            """
                            MERGE (p:Person {id: $actor_id})
                            ON CREATE SET p.name = $name, p.popularity = $pop, p.adult = $adult
                            """,
                            {"actor_id": actor_id, "name": person_info["name"],
                             "pop": person_info["popularity"], "adult": person_info["adult"]}
                        )
                    else:
                        session.run(
                            """
                            MERGE (p:Person {id: $actor_id})                                """,
                            {"actor_id": actor_id}
                        )
                    existing_person_ids.add(actor_id)

                # Create the ACTED_IN relationship between the Person and the Movie
                session.run(
                    """
                    MATCH (p:Person {id: $actor_id})
                    MATCH (m:Movie {id: $movie_id})
                    MERGE (p)-[:ACTED_IN]->(m)
                    """,
                    {"actor_id": actor_id, "movie_id": movie_id}
                )
                print("actor_id: ", actor_id)

print("Actor-Movie relationships import complete.")
driver.close()
print("ETL Process Completed Successfully.")

