import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = "postgresql://postgres.umqcumxtjtinghhzkhtf:CLOUDTRIP-123@aws-1-eu-central-1.pooler.supabase.com:5432/postgres"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

def ensure_users_table():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_data (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
    finally:
        conn.close()

def ensure_traveller_table():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS traveller_data (
                traveller_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users_data(user_id),
                full_name VARCHAR(255) NOT NULL,
                passport_number VARCHAR(50),
                nationality VARCHAR(100),
                age INTEGER,
                gender VARCHAR(20),
                email VARCHAR(255),
                phone_number VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
    finally:
        conn.close()

def ensure_payments_table():
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users_data(user_id),
                flight_id INTEGER REFERENCES flights(flight_id),
                amount NUMERIC NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                payment_status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
    finally:
        conn.close()

def add_travellers(user_id, travellers_list):
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        for traveller in travellers_list:
            cur.execute("""
                INSERT INTO traveller_data
                (user_id, full_name, passport_number, nationality, age, gender, email, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                traveller.get("full_name"),
                traveller.get("passport_number"),
                traveller.get("nationality"),
                traveller.get("age"),
                traveller.get("gender"),
                traveller.get("email"),
                traveller.get("phone_number")
            ))
        conn.commit()
        cur.close()
    finally:
        conn.close()

def init_db():
    ensure_users_table()
    ensure_traveller_table()
    ensure_payments_table()

if __name__ == "__main__":
    init_db()
    print("Database ready")