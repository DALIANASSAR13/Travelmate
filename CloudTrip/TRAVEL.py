from flask import Flask, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

DATABASE_URL = "postgresql://postgres:BkrcZoomvzLacyxsMInqHGdSttjGCwdh@turntable.proxy.rlwy.net:48669/railway"

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

def ensure_users_table():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users_data (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cursor.close()
            print("'users_data' table ready!")
        except Exception as e:
            print("Error creating 'users_data' table:", e)
        finally:
            conn.close()

@app.route('/')
def home():
    if 'user_id' in session:
        return f"<h1>Welcome, {session['username']}!</h1><a href='/logout'>Logout</a>"
    return '''
        <h1>Welcome to CloudTrip</h1>
        <a href="/signup">Signup</a> | <a href="/login">Login</a>
    '''

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not username or not email or not password:
            return "All fields are required!"

        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        if not conn:
            return "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users_data WHERE email=%s", (email,))
            if cursor.fetchone():
                conn.close()
                return "Email already registered!"

            cursor.execute(
                "INSERT INTO users_data (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id",
                (username, email, hashed_pw)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('home'))
        except Exception as e:
            print("Signup error:", e)
            return f"Signup error: {e}"

    return '''
        <h2>Signup</h2>
        <form method="POST">
            Username: <input type="text" name="username"><br><br>
            Email: <input type="text" name="email"><br><br>
            Password: <input type="password" name="password"><br><br>
            <button type="submit">Signup</button>
        </form>
        <br>
        <a href="/login">Go to Login</a>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not email or not password:
            return "Email and password are required!"

        conn = get_db_connection()
        if not conn:
            return "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, password_hash, username FROM users_data WHERE email=%s", (email,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if not row:
                return "Email not found. Please signup first."

            user_id, stored_hash, username = row
            if check_password_hash(stored_hash, password):
                session['user_id'] = user_id
                session['username'] = username
                return redirect(url_for('home'))
            else:
                return "Invalid email or password."
        except Exception as e:
            print("Login error:", e)
            return f"Login error: {e}"

    return '''
        <h2>Login</h2>
        <form method="POST">
            Email: <input type="text" name="email"><br><br>
            Password: <input type="password" name="password"><br><br>
            <button type="submit">Login</button>
        </form>
        <br>
        <a href="/signup">Go to Signup</a>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    ensure_users_table()
    app.run(debug=True)