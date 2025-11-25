from flask import Flask, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import pyodbc
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")
print("Database URL loaded:", database_url)

app = Flask(__name__)

def get_db_connection():
    try:
        conn = pyodbc.connect(database_url)
        print("Connected to SQL Server")
        return conn
    except Exception as e:
        print("Connection failed:", e)
        return None

def ensure_users_data_table():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users_data')
                CREATE TABLE users_data (
                    user_id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(255) NOT NULL,
                    email NVARCHAR(255) NOT NULL UNIQUE,
                    password_hash NVARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            print("users_data table checked/created")
        except Exception as e:
            print("Error creating users_data table:", e)
        finally:
            conn.close()

ensure_users_data_table()

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not username or not email or not password:
            return "All fields are required!"

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users_data WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return "Email already registered"

            hashed_pw = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users_data (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, hashed_pw)
            )
            conn.commit()
            conn.close()
            return "Signup successful! You can now log in"
        except Exception as e:
            print("Signup error:", e)
            return f"Signup error: {e}"

    return '''
        <h2>Signup Page</h2>
        <form method="POST">
            Username: <input type="text" name="username"><br><br>
            Email: <input type="text" name="email"><br><br>
            Password: <input type="password" name="password"><br><br>
            <button type="submit">Signup</button>
        </form>
        <br>
        <a href="/login">Go to Login</a>
    '''

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not email or not password:
            return "Email and password are required!"

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, username FROM users_data WHERE email = ?", (email,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                return "Email not found. Please sign up first."

            stored_hash, username = row
            if check_password_hash(stored_hash, password):
                conn.close()
                return f"Welcome, {username}! Login successful."
            else:
                conn.close()
                return "Invalid email or password."
        except Exception as e:
            print("Login error:", e)
            return f"Login error: {e}"

    return '''
        <h2>Login Page</h2>
        <form method="POST">
            Email: <input type="text" name="email"><br><br>
            Password: <input type="password" name="password"><br><br>
            <button type="submit">Login</button>
        </form>
        <br>
        <a href="/signup">Go to Signup</a>
    '''

# ---------- SEARCH ----------
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        trip_type = request.form.get('trip_type')
        from_country = request.form.get('from_country')
        to_country = request.form.get('to_country')
        depart_date = request.form.get('depart_date')
        return_date = request.form.get('return_date')
        travellers = request.form.get('travellers')

        print(trip_type, from_country, to_country, depart_date, return_date, travellers)
        return "Search data received!"

    return "Search form placeholder (coming soon)"

# ---------- VIEW USERS (FOR TESTING ONLY) ----------
@app.route('/view_users')
def view_users():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed"

    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email, password_hash FROM users_data")
    rows = cursor.fetchall()
    conn.close()

    result = "<h2>Users Table</h2><table border='1'><tr><th>ID</th><th>Username</th><th>Email</th><th>Password Hash</th></tr>"
    for row in rows:
        result += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    result += "</table>"
    return result

if __name__ == '__main__':
    app.run(debug=True)