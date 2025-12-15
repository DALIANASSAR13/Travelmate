from werkzeug.security import generate_password_hash, check_password_hash  # لو حبيت تستخدمه هنا
import pandas as pd
import psycopg2
import random
import os

# =========================
# DB CONFIG
# =========================
DATABASE_URL = "postgresql://postgres:BkrcZoomvzLacyxsMInqHGdSttjGCwdh@turntable.proxy.rlwy.net:48669/railway"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "Dataset")


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None


# =========================
# LOAD DATASETS (once)
# =========================
airports_df = pd.read_excel(os.path.join(DATASET_DIR, "filtered_airports.xlsx"))
routes_df = pd.read_excel(os.path.join(DATASET_DIR, "filtered_routes.xlsx"))
airlines_df = pd.read_excel(os.path.join(DATASET_DIR, "filtered_airlines.xlsx"))
airplanes_df = pd.read_excel(os.path.join(DATASET_DIR, "filtered_airplanes.xlsx"))

airports_df.columns = airports_df.columns.str.strip()
routes_df.columns = routes_df.columns.str.strip()
airlines_df.columns = airlines_df.columns.str.strip()
airplanes_df.columns = airplanes_df.columns.str.strip()


# =========================
# TABLE CREATION
# =========================
def ensure_users_table():
    conn = get_db_connection()
    if not conn:
        return
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
    conn.close()


def ensure_traveller_table():
    conn = get_db_connection()
    if not conn:
        return
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
    conn.close()


def ensure_airports_table():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            airport_id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            city VARCHAR(255),
            country VARCHAR(255),
            iata VARCHAR(10) UNIQUE,
            latitude FLOAT,
            longitude FLOAT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def ensure_flights_table():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_id SERIAL PRIMARY KEY,
            flight_name VARCHAR(100),
            airline VARCHAR(255),
            from_airport VARCHAR(10),
            to_airport VARCHAR(10),
            departure_time VARCHAR(50),
            arrival_time VARCHAR(50),
            duration VARCHAR(50),
            price NUMERIC,
            airplane VARCHAR(100)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def ensure_payments_table():
    conn = get_db_connection()
    if not conn:
        return
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
    conn.close()


# =========================
# DATA INSERTION (WITH CHECK)
# =========================
def insert_airports():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()

    # نشوف الأول لو فيه داتا ولا لأ
    cur.execute("SELECT COUNT(*) FROM airports;")
    count = cur.fetchone()[0]
    if count > 0:
        # فيه مطارات بالفعل → متعملش حاجة
        cur.close()
        conn.close()
        return

    for _, row in airports_df.iterrows():
        cur.execute("""
            INSERT INTO airports (name, city, country, iata, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (iata) DO NOTHING;
        """, (
            row["Name"],
            row["City"],
            row["Country"],
            row["IATA"],
            row["Latitude"],
            row["Longitude"]
        ))
    conn.commit()
    cur.close()
    conn.close()


def insert_flights():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()

    # نشوف الأول لو فيه رحلات ولا لأ
    cur.execute("SELECT COUNT(*) FROM flights;")
    count = cur.fetchone()[0]
    if count > 0:
        cur.close()
        conn.close()
        return

    for _, route in routes_df.iterrows():
        airline_row = airlines_df.sample(1).iloc[0]
        airplane_row = airplanes_df.sample(1).iloc[0]

        flight_name = f"{airline_row['IATA']}{random.randint(100,999)}"
        from_airport = route['Source airport']
        to_airport = route['Destination airport']
        departure_time = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
        arrival_time = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
        duration = f"{random.randint(1,12)}h {random.randint(0,59)}m"
        price = random.randint(100,1500)
        airplane = airplane_row['Name']

        cur.execute("""
            INSERT INTO flights
            (flight_name, airline, from_airport, to_airport, departure_time, arrival_time, duration, price, airplane)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            flight_name,
            airline_row['Name'],
            from_airport,
            to_airport,
            departure_time,
            arrival_time,
            duration,
            price,
            airplane
        ))

    conn.commit()
    cur.close()
    conn.close()


def add_travellers(user_id, travellers_list):
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    for traveller in travellers_list:
        cur.execute("""
            INSERT INTO traveller_data
            (user_id, full_name, passport_number, nationality, age, gender, email, phone_number)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
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
    conn.close()


# =========================
# ONE FUNCTION TO INIT ALL
# =========================
def init_db(seed_data: bool = True):
    ensure_users_table()
    ensure_traveller_table()
    ensure_airports_table()
    ensure_flights_table()
    ensure_payments_table()
    if seed_data:
        insert_airports()
        insert_flights()
