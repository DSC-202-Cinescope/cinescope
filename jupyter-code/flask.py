from flask import Flask, jsonify
import psycopg2
from config import config

app = Flask(__name__)

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # Read connection parameters
        params = config()

        # Connect to PostgreSQL
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # Execute a statement
        cur.execute('SELECT version()')
        db_version = cur.fetchone()

        # Close communication
        cur.close()
        conn.close()

        return db_version[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return str(error)

@app.route('/db-version', methods=['GET'])
def db_version():
    """API endpoint to get PostgreSQL version"""
    version = connect()
    return jsonify({"PostgreSQL Version": version})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
