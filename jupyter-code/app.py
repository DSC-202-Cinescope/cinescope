import redis
import json
import decimal
import psycopg2
from config import config
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask import session as flask_session
from neo4j import GraphDatabase
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
redis_client = redis.Redis(host="redis-0.redis", port=6379, decode_responses=True)

# Neo4j connection 
neo4j_uri = "bolt://neo4j:7687"
neo4j_username = "neo4j"
neo4j_password = ""
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

LANGUAGE_MAP = {"aa":"Afar--Ethiopia","ab":"Abkhazian--Georgia","af":"Afrikaans--South Africa","ak":"Akan--Ghana","am":"Amharic--Ethiopia","an":"Aragonese--Spain","ar":"Arabic--Saudi Arabia","as":"Assamese--India","av":"Avaric--Russia","ay":"Aymara--Bolivia","az":"Azerbaijani--Azerbaijan","ba":"Bashkir--Russia","be":"Belarusian--Belarus","bg":"Bulgarian--Bulgaria","bh":"Bihari--India","bi":"Bislama--Vanuatu","bm":"Bambara--Mali","bn":"Bengali--Bangladesh","bo":"Tibetan--China","br":"Breton--France","bs":"Bosnian--Bosnia and Herzegovina","ca":"Catalan--Spain","ce":"Chechen--Russia","ch":"Chamorro--Guam","co":"Corsican--France","cr":"Cree--Canada","cs":"Czech--Czech Republic","cu":"Church Slavic--Russia","cv":"Chuvash--Russia","cy":"Welsh--United Kingdom","da":"Danish--Denmark","de":"German--Germany","dv":"Divehi--Maldives","dz":"Dzongkha--Bhutan","ee":"Ewe--Togo","el":"Greek--Greece","en":"English--United Kingdom","eo":"Esperanto--International","es":"Spanish--Spain","et":"Estonian--Estonia","eu":"Basque--Spain","fa":"Persian--Iran","ff":"Fulah--Senegal","fi":"Finnish--Finland","fj":"Fijian--Fiji","fo":"Faroese--Faroe Islands","fr":"French--France","fy":"Western Frisian--Netherlands","ga":"Irish--Ireland","gd":"Scottish Gaelic--United Kingdom","gl":"Galician--Spain","gn":"Guarani--Paraguay","gu":"Gujarati--India","gv":"Manx--Isle of Man","ha":"Hausa--Nigeria","he":"Hebrew--Israel","hi":"Hindi--India","ho":"Hiri Motu--Papua New Guinea","hr":"Croatian--Croatia","ht":"Haitian Creole--Haiti","hu":"Hungarian--Hungary","hy":"Armenian--Armenia","hz":"Herero--Namibia","ia":"Interlingua--International","id":"Indonesian--Indonesia","ie":"Interlingue--International","ig":"Igbo--Nigeria","ii":"Sichuan Yi--China","ik":"Inupiaq--Alaska","io":"Ido--International","is":"Icelandic--Iceland","it":"Italian--Italy","iu":"Inuktitut--Canada","ja":"Japanese--Japan","jv":"Javanese--Indonesia","ka":"Georgian--Georgia","kg":"Kongo--Republic of Congo","ki":"Kikuyu--Kenya","kj":"Kwanyama--Angola","kk":"Kazakh--Kazakhstan","kl":"Greenlandic--Greenland","km":"Khmer--Cambodia","kn":"Kannada--India","ko":"Korean--South Korea","kr":"Kanuri--Nigeria","ks":"Kashmiri--India","ku":"Kurdish--Turkey","kv":"Komi--Russia","kw":"Cornish--United Kingdom","ky":"Kyrgyz--Kyrgyzstan","la":"Latin--Vatican","lb":"Luxembourgish--Luxembourg","lg":"Ganda--Uganda","li":"Limburgish--Netherlands","ln":"Lingala--DR Congo","lo":"Lao--Laos","lt":"Lithuanian--Lithuania","lu":"Luba-Katanga--DR Congo","lv":"Latvian--Latvia","mg":"Malagasy--Madagascar","mh":"Marshallese--Marshall Islands","mi":"Maori--New Zealand","mk":"Macedonian--North Macedonia","ml":"Malayalam--India","mn":"Mongolian--Mongolia","mr":"Marathi--India","ms":"Malay--Malaysia","mt":"Maltese--Malta","my":"Burmese--Myanmar","na":"Nauru--Nauru","nb":"Norwegian Bokmål--Norway","nd":"North Ndebele--Zimbabwe","ne":"Nepali--Nepal","ng":"Ndonga--Namibia","nl":"Dutch--Netherlands","nn":"Norwegian Nynorsk--Norway","no":"Norwegian--Norway","nr":"South Ndebele--South Africa","nv":"Navajo--United States","ny":"Chichewa--Malawi","oc":"Occitan--France","oj":"Ojibwe--Canada","om":"Oromo--Ethiopia","or":"Odia--India","os":"Ossetian--Russia","pa":"Punjabi--India","pi":"Pali--India","pl":"Polish--Poland","ps":"Pashto--Afghanistan","pt":"Portuguese--Portugal","qu":"Quechua--Peru","rm":"Romansh--Switzerland","rn":"Kirundi--Burundi","ro":"Romanian--Romania","ru":"Russian--Russia","rw":"Kinyarwanda--Rwanda","sa":"Sanskrit--India","sc":"Sardinian--Italy","sd":"Sindhi--Pakistan","se":"Northern Sami--Norway","sg":"Sango--Central African Republic","si":"Sinhala--Sri Lanka","sk":"Slovak--Slovakia","sl":"Slovenian--Slovenia","sm":"Samoan--Samoa","sn":"Shona--Zimbabwe","so":"Somali--Somalia","sq":"Albanian--Albania","sr":"Serbian--Serbia","ss":"Swati--Eswatini","st":"Southern Sotho--Lesotho","su":"Sundanese--Indonesia","sv":"Swedish--Sweden","sw":"Swahili--Kenya","ta":"Tamil--India","te":"Telugu--India","tg":"Tajik--Tajikistan","th":"Thai--Thailand","ti":"Tigrinya--Eritrea","tk":"Turkmen--Turkmenistan","tl":"Tagalog--Philippines","tn":"Tswana--Botswana","to":"Tongan--Tonga","tr":"Turkish--Turkey","ts":"Tsonga--Mozambique","tt":"Tatar--Russia","tw":"Twi--Ghana","ty":"Tahitian--French Polynesia","ug":"Uyghur--China","uk":"Ukrainian--Ukraine","ur":"Urdu--Pakistan","uz":"Uzbek--Uzbekistan","ve":"Venda--South Africa","vi":"Vietnamese--Vietnam","vo":"Volapük--International","wa":"Walloon--Belgium","wo":"Wolof--Senegal","xh":"Xhosa--South Africa","yi":"Yiddish--Israel","yo":"Yoruba--Nigeria","za":"Zhuang--China","zh":"Chinese--China","zu":"Zulu--South Africa"
}

def decimal_default(obj):
    """Convert Decimal to float or string for JSON serialization."""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError("Type not serializable")

def getGenres(schema, table, column):
    """Return the column names of the given table."""
    conn = None
    genre_names = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        sql_command = f"SELECT {column} FROM {schema}.{table};"
        cache_key = f"genres_query:{sql_command}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
            
        cur.execute(sql_command)
        genre_names = [row[0] for row in cur.fetchall()]
        redis_client.setex(cache_key, 600000, json.dumps(genre_names))
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            conn.close()
    
    return genre_names

def getGenreId(schema, table, genre_name):
    """genre ID corresponding to the selected genre name."""
    conn = None
    genre_id = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        sql_command = f"SELECT id FROM {schema}.{table} WHERE name = %s;"
        
        cache_key = f"genre_id_{genre_name}_query:{sql_command}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            print("cached result: ")
            return json.loads(cached_result)
            
        cur.execute(sql_command, (genre_name,))
        result = cur.fetchone() 

        if result:
            genre_id = result[0]
        redis_client.setex(cache_key, 600000, json.dumps(genre_id))
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            conn.close()
    
    return genre_id

def getLanguages():
    conn = None
    languages = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        sql_command = f"SELECT DISTINCT original_language FROM movies WHERE original_language IS NOT NULL ORDER BY original_language;"

        cache_key = f"lang_query:{sql_command}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            print("cached result: ")
            return json.loads(cached_result)
            
        cur.execute(sql_command)
        rows = cur.fetchall()

        languages = [(row[0], LANGUAGE_MAP.get(row[0], row[0])) for row in rows]
        redis_client.setex(cache_key, 600000, json.dumps(languages))
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            conn.close()
    
    return languages

def getMoviesByGenreAndLanguage(genre_id, language):
    conn = None
    movies = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        with open("../sql/genre-lookup.sql", "r") as file:
            sql_query = file.read()

        sql_query = sql_query.replace("{GENRE_ID}", str(genre_id))
        sql_query = sql_query.replace("{LANGUAGE_PARAM}", language)

        cache_key = f"{genre_id}_{language}_query:{sql_query}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
            
        cur.execute(sql_query)
        movies = cur.fetchall()

        redis_client.setex(cache_key, 600000, json.dumps(movies, default=decimal_default))
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None:
            conn.close()

    return movies

@app.route('/', methods=["GET", "POST"])
def index():
    genres = getGenres("public", "genre", "name")
    languages = getLanguages()  # The new function
    
    selected_genre = None
    selected_language = None
    movies = []

    if request.method == "POST":
        selected_genre = request.form.get("genre") 
        selected_language = request.form.get("language")

        genre_id = getGenreId("public", "genre", selected_genre)

        if genre_id and selected_language:
            movies = getMoviesByGenreAndLanguage(genre_id, selected_language)
            flask_session['genre_id'] = genre_id
            flask_session['selected_language'] = selected_language

    return render_template("index.html",
                           genres=genres,
                           languages=languages,
                           selected_genre=selected_genre,
                           selected_language=selected_language,
                           movies=movies)

@app.route('/api/graph', methods=['GET'])
def get_graph():
    # Expect a genre parameter from the request
    genre = request.args.get("genre", None)
    if not genre:
        return jsonify({"error": "genre parameter is required"}), 400

    # Retrieve a valid genre ID using your existing function.
    genre_id = flask_session.get('genre_id', None)
    lang = flask_session.get('selected_language', None)

    if not genre_id:
        return jsonify({"error": f"Genre '{genre}' not found."}), 404

    movies = getMoviesByGenreAndLanguage(genre_id, lang)
    movie_list = [movie[0] for movie in movies]

    graph_data = {"nodes": [], "edges": []}
    node_ids = set()
    edge_ids = set()
    
    
    with driver.session() as session:
        # Query Neo4j: find top 5 movies for the given genre (ignoring language)

        query = """
        MATCH (g:Genre)<-[:HAS_GENRE]-(m:Movie)
        WHERE m.title IN $movie_list
        MATCH (a:Person)-[:ACTED_IN]->(m)
        WHERE a.popularity > 1
        RETURN g, m, a
        """

        result = session.run(query, {"movie_list": movie_list})

        for record in result:
            g = record["g"]
            m = record["m"]
            a = record["a"]

            genre_node_id = f"Genre_{g['name']}"
            if genre_node_id not in node_ids:
                graph_data["nodes"].append({
                    "id": genre_node_id,
                    "label": g["name"],
                    "type": "Genre"
                })
                node_ids.add(genre_node_id)

            movie_node_id = f"Movie_{m['id']}"
            if movie_node_id not in node_ids:
                graph_data["nodes"].append({
                    "id": movie_node_id,
                    "label": m.get("title", "Untitled"),
                    "type": "Movie"
                })
                node_ids.add(movie_node_id)

            if a is not None:
                actor_node_id = f"Actor_{a['id']}"
                if actor_node_id not in node_ids:
                    graph_data["nodes"].append({
                        "id": actor_node_id,
                        "label": a.get("name", "Unknown"),
                        "type": "Actor"
                    })
                    node_ids.add(actor_node_id)

            edge_key = (movie_node_id, genre_node_id)
            if edge_key not in edge_ids:
                graph_data["edges"].append({
                    "source": movie_node_id,
                    "target": genre_node_id,
                    "label": "HAS_GENRE"
                })
                edge_ids.add(edge_key)

            if a is not None:
                edge_key = (actor_node_id, movie_node_id)
                if edge_key not in edge_ids:
                    graph_data["edges"].append({
                        "source": actor_node_id,
                        "target": movie_node_id,
                        "label": "ACTED_IN"
                    })
                    edge_ids.add(edge_key)
        return jsonify(graph_data)
 
def get_genre_movie_counts():
    query = """
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Movie)
    MATCH (a:Person)-[:ACTED_IN]->(m)
    WHERE a.popularity > 5
    RETURN g.name, COUNT(DISTINCT m) AS movie_count
    ORDER BY movie_count DESC
    LIMIT 50
    """
    with driver.session() as session:
        result = session.run(query)
        genre_movie_counts = []
        for record in result:
            genre_movie_counts.append({
                'genre': record['g.name'],
                'movie_count': record['movie_count']
            })
    return genre_movie_counts

@app.route('/api/genre_movie_counts', methods=['GET'])
def get_genre_movie_counts_api():
    try:
        genre_movie_counts = get_genre_movie_counts()  # Call the function that gets genre movie counts
        return jsonify(genre_movie_counts)  # Return the data in JSON format
    except Exception as e:
        app.logger.error("Error in get_genre_movie_counts_api: %s", e)
        return jsonify({"error": "Failed to fetch genre movie counts"}), 500
        

def get_genre_actor_pop():
    query = """
    MATCH (a:Person)-[:ACTED_IN]->(m:Movie)-[:HAS_GENRE]->(g:Genre)
    WHERE a.popularity > 5
    WITH g.name AS genre, a
    ORDER BY a.popularity DESC
    RETURN genre, COLLECT(a.name)[0] AS most_popular_actor
    LIMIT 20
    """
    with driver.session() as session:
        result = session.run(query)
        genre_actor_pop = []
        for record in result:
            genre_actor_pop.append({
                'genre': record['genre'],
                'most_popular_actor': record['most_popular_actor']
            })
    return genre_actor_pop

@app.route('/api/genre_actor_pop', methods=['GET'])
def get_genre_actor_pop_api():
    try:
        genre_actor_pop = get_genre_actor_pop()  # Call the function that gets genre movie counts
        return jsonify(genre_actor_pop)  # Return the data in JSON format
    except Exception as e:
        app.logger.error("Error in get_genre_movie_counts_api: %s", e)
        return jsonify({"error": "Failed to fetch genre movie counts"}), 500

@app.route('/api/graph2', methods=['GET'])
def get_graph2():
    # Expect a genre parameter from the request
    genre = request.args.get("genre", None)
    if not genre:
        return jsonify({"error": "genre parameter is required"}), 400

    # Retrieve a valid genre ID using your existing function.
    genre_id = flask_session.get('genre_id', None)
    lang = flask_session.get('selected_language', None)

    if not genre_id:
        return jsonify({"error": f"Genre '{genre}' not found."}), 404

    cache_key = f"graphactor_query:{genre}"
    cached_result = redis_client.get(cache_key)
    #if cached_result:
    #    return jsonify(json.loads(cached_result))

    graph_data2 = {"nodes": [], "edges": []}
    
    with driver.session() as session:
        query = """
        MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre {name: $genre})
        WITH m, g
        MATCH (a1:Person)-[:ACTED_IN]->(m)<-[:ACTED_IN]-(a2:Person)
        WHERE a1.popularity > 0.5 
          AND a2.popularity > 0.5 
          AND a1 <> a2
        WITH a1, a2, COUNT(m) AS shared_movies, COLLECT(m.title) AS movie_titles
        WHERE shared_movies > 1
        RETURN a1, a2, {movies: shared_movies} AS relationship_data, movie_titles
        LIMIT 5000;
        """
        result = session.run(query, {"genre": genre}, timeout=120)

        if not result:
            return jsonify({"error": "No data found for the given genre."}), 404
        
        actors_sharing_movies_data = []
        for record in result:
            actor1 = record["a1"]["name"]
            actor2 = record["a2"]["name"]
            shared_movies = record["relationship_data"]["movies"]
            movie_titles = record["movie_titles"]
            
            # Add nodes for actors
            graph_data2["nodes"].append({"id": f"Actor_{actor1}", "label": actor1, "type": "Actor"})
            graph_data2["nodes"].append({"id": f"Actor_{actor2}", "label": actor2, "type": "Actor"})
            
            # Add the shared relationship
            graph_data2["edges"].append({"source": f"Actor_{actor1}", "target": f"Actor_{actor2}", "label": f"Shared Movies: {shared_movies}\nMovies: {', '.join(movie_titles)}"})
        if not record:
            return jsonify({"error": "Missing data"}), 404
        redis_client.setex(cache_key, 1000, json.dumps(graph_data2))
    return jsonify(graph_data2)

def handle_exception(e):
    # Log the exception details
    app.logger.error("Unhandled Exception: %s", traceback.format_exc())
    # Return a JSON response with error details if in debug mode, otherwise a generic message
    if app.debug:
        return jsonify(error=str(e), traceback=traceback.format_exc()), 500
    else:
        return jsonify(error="Internal Server Error"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    