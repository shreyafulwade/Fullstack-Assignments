
import psycopg2

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="user_login_db",
            user="postgres",
            password="root",
            port="5432"
        )

        return conn

    except Exception as e:
        print("Database Connection Error:", e)
        return None
