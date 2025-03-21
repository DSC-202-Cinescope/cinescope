CREATE TABLE movies (
    adult BOOLEAN,
    backdrop_path TEXT,
    belongs_to_collection TEXT,
    budget BIGINT,
    genres JSONB,
    homepage TEXT,
    id SERIAL PRIMARY KEY,
    imdb_id VARCHAR(15),
    origin_country TEXT[],
    original_language VARCHAR(10),
    original_title TEXT,
    overview TEXT,
    popularity NUMERIC(10, 5),
    poster_path TEXT,
    production_companies JSONB,
    production_countries JSONB,
    release_date DATE,
    revenue BIGINT,
    runtime INTEGER,
    spoken_languages JSONB,
    status VARCHAR(50),
    tagline TEXT,
    title TEXT,
    video BOOLEAN,
    vote_average NUMERIC(3, 1),
S movies (id) ON DELETE CASCADE
);

CREATE TABLE actorsINTEGER  adult BOOLEAN,
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    popularity NUMERIC(10, 5)
);

CREATE TABLE actor_movies (
    actor_id INTEGER,
    movie_id INTEGER,
    PRIMARY KEY (actor_id, movie_id),
    FOREIGN KEY (actor_id) REFERENCES actors (id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
);

CREATE TABLE genre
  id SERIAL PRIMARY KEY,
  name VARCHAR(50)
);






