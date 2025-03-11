import psycopg2
from config import config
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

LANGUAGE_MAP = {"aa":"Afar--Ethiopia","ab":"Abkhazian--Georgia","af":"Afrikaans--South Africa","ak":"Akan--Ghana","am":"Amharic--Ethiopia","an":"Aragonese--Spain","ar":"Arabic--Saudi Arabia","as":"Assamese--India","av":"Avaric--Russia","ay":"Aymara--Bolivia","az":"Azerbaijani--Azerbaijan","ba":"Bashkir--Russia","be":"Belarusian--Belarus","bg":"Bulgarian--Bulgaria","bh":"Bihari--India","bi":"Bislama--Vanuatu","bm":"Bambara--Mali","bn":"Bengali--Bangladesh","bo":"Tibetan--China","br":"Breton--France","bs":"Bosnian--Bosnia and Herzegovina","ca":"Catalan--Spain","ce":"Chechen--Russia","ch":"Chamorro--Guam","co":"Corsican--France","cr":"Cree--Canada","cs":"Czech--Czech Republic","cu":"Church Slavic--Russia","cv":"Chuvash--Russia","cy":"Welsh--United Kingdom","da":"Danish--Denmark","de":"German--Germany","dv":"Divehi--Maldives","dz":"Dzongkha--Bhutan","ee":"Ewe--Togo","el":"Greek--Greece","en":"English--United Kingdom","eo":"Esperanto--International","es":"Spanish--Spain","et":"Estonian--Estonia","eu":"Basque--Spain","fa":"Persian--Iran","ff":"Fulah--Senegal","fi":"Finnish--Finland","fj":"Fijian--Fiji","fo":"Faroese--Faroe Islands","fr":"French--France","fy":"Western Frisian--Netherlands","ga":"Irish--Ireland","gd":"Scottish Gaelic--United Kingdom","gl":"Galician--Spain","gn":"Guarani--Paraguay","gu":"Gujarati--India","gv":"Manx--Isle of Man","ha":"Hausa--Nigeria","he":"Hebrew--Israel","hi":"Hindi--India","ho":"Hiri Motu--Papua New Guinea","hr":"Croatian--Croatia","ht":"Haitian Creole--Haiti","hu":"Hungarian--Hungary","hy":"Armenian--Armenia","hz":"Herero--Namibia","ia":"Interlingua--International","id":"Indonesian--Indonesia","ie":"Interlingue--International","ig":"Igbo--Nigeria","ii":"Sichuan Yi--China","ik":"Inupiaq--Alaska","io":"Ido--International","is":"Icelandic--Iceland","it":"Italian--Italy","iu":"Inuktitut--Canada","ja":"Japanese--Japan","jv":"Javanese--Indonesia","ka":"Georgian--Georgia","kg":"Kongo--Republic of Congo","ki":"Kikuyu--Kenya","kj":"Kwanyama--Angola","kk":"Kazakh--Kazakhstan","kl":"Greenlandic--Greenland","km":"Khmer--Cambodia","kn":"Kannada--India","ko":"Korean--South Korea","kr":"Kanuri--Nigeria","ks":"Kashmiri--India","ku":"Kurdish--Turkey","kv":"Komi--Russia","kw":"Cornish--United Kingdom","ky":"Kyrgyz--Kyrgyzstan","la":"Latin--Vatican","lb":"Luxembourgish--Luxembourg","lg":"Ganda--Uganda","li":"Limburgish--Netherlands","ln":"Lingala--DR Congo","lo":"Lao--Laos","lt":"Lithuanian--Lithuania","lu":"Luba-Katanga--DR Congo","lv":"Latvian--Latvia","mg":"Malagasy--Madagascar","mh":"Marshallese--Marshall Islands","mi":"Maori--New Zealand","mk":"Macedonian--North Macedonia","ml":"Malayalam--India","mn":"Mongolian--Mongolia","mr":"Marathi--India","ms":"Malay--Malaysia","mt":"Maltese--Malta","my":"Burmese--Myanmar","na":"Nauru--Nauru","nb":"Norwegian Bokmål--Norway","nd":"North Ndebele--Zimbabwe","ne":"Nepali--Nepal","ng":"Ndonga--Namibia","nl":"Dutch--Netherlands","nn":"Norwegian Nynorsk--Norway","no":"Norwegian--Norway","nr":"South Ndebele--South Africa","nv":"Navajo--United States","ny":"Chichewa--Malawi","oc":"Occitan--France","oj":"Ojibwe--Canada","om":"Oromo--Ethiopia","or":"Odia--India","os":"Ossetian--Russia","pa":"Punjabi--India","pi":"Pali--India","pl":"Polish--Poland","ps":"Pashto--Afghanistan","pt":"Portuguese--Portugal","qu":"Quechua--Peru","rm":"Romansh--Switzerland","rn":"Kirundi--Burundi","ro":"Romanian--Romania","ru":"Russian--Russia","rw":"Kinyarwanda--Rwanda","sa":"Sanskrit--India","sc":"Sardinian--Italy","sd":"Sindhi--Pakistan","se":"Northern Sami--Norway","sg":"Sango--Central African Republic","si":"Sinhala--Sri Lanka","sk":"Slovak--Slovakia","sl":"Slovenian--Slovenia","sm":"Samoan--Samoa","sn":"Shona--Zimbabwe","so":"Somali--Somalia","sq":"Albanian--Albania","sr":"Serbian--Serbia","ss":"Swati--Eswatini","st":"Southern Sotho--Lesotho","su":"Sundanese--Indonesia","sv":"Swedish--Sweden","sw":"Swahili--Kenya","ta":"Tamil--India","te":"Telugu--India","tg":"Tajik--Tajikistan","th":"Thai--Thailand","ti":"Tigrinya--Eritrea","tk":"Turkmen--Turkmenistan","tl":"Tagalog--Philippines","tn":"Tswana--Botswana","to":"Tongan--Tonga","tr":"Turkish--Turkey","ts":"Tsonga--Mozambique","tt":"Tatar--Russia","tw":"Twi--Ghana","ty":"Tahitian--French Polynesia","ug":"Uyghur--China","uk":"Ukrainian--Ukraine","ur":"Urdu--Pakistan","uz":"Uzbek--Uzbekistan","ve":"Venda--South Africa","vi":"Vietnamese--Vietnam","vo":"Volapük--International","wa":"Walloon--Belgium","wo":"Wolof--Senegal","xh":"Xhosa--South Africa","yi":"Yiddish--Israel","yo":"Yoruba--Nigeria","za":"Zhuang--China","zh":"Chinese--China","zu":"Zulu--South Africa"
}


def getGenres(schema, table, column):
    """Return the column names of the given table."""
    conn = None
    genre_names = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        sql_command = f"SELECT {column} FROM {schema}.{table};"

        cur.execute(sql_command)
        genre_names = [row[0] for row in cur.fetchall()]

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
        cur.execute(sql_command, (genre_name,))
        result = cur.fetchone() 

        if result:
            genre_id = result[0]

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

        cur.execute("""
            SELECT DISTINCT original_language
            FROM movies
            WHERE original_language IS NOT NULL
            ORDER BY original_language;
        """)
        rows = cur.fetchall()

        languages = [(row[0], LANGUAGE_MAP.get(row[0], row[0])) for row in rows]

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

        with open("../sql/genre-lookup-Copy1.sql", "r") as file:
            sql_query = file.read()

        sql_query = sql_query.replace("{GENRE_ID}", str(genre_id))
        sql_query = sql_query.replace("{LANGUAGE_PARAM}", language)

        cur.execute(sql_query)
        movies = cur.fetchall()
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

    return render_template("index.html",
                           genres=genres,
                           languages=languages,
                           selected_genre=selected_genre,
                           selected_language=selected_language,
                           movies=movies)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    