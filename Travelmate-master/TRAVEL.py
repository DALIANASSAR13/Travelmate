from flask import Flask, request, redirect, url_for, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

# -----------------------------
# Configuration & App Setup
# -----------------------------
# DATABASE URL for PostgreSQL connection
DATABASE_URL = "postgresql://postgres:BkrcZoomvzLacyxsMInqHGdSttjGCwdh@turntable.proxy.rlwy.net:48669/railway"

# Initialize Flask app and set secret key for session management
app = Flask(__name__)
app.secret_key = os.urandom(24)


# -----------------------------
# Database Connection Utility
# -----------------------------
# Function to get a database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None


# -----------------------------
# Database Initialization
# -----------------------------
# Ensure the 'users_data' table exists in the database
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


# -----------------------------
# Home Route
# -----------------------------
# Displays the home page, shows username if logged in
@app.route('/')
def home():
    username = session.get('username')
    return render_template('index.html', username=username)


# -----------------------------
# Signup Route
# -----------------------------
# Handles user registration (GET shows form, POST processes registration)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Validate required fields
        if not first_name or not email or not password:
            return "All fields are required!"

        # Combine first and last name
        username = f"{first_name} {last_name}".strip()

        # Hash the password
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        if not conn:
            return "Database connection failed"

        try:
            cursor = conn.cursor()

            # Check if email is already registered
            cursor.execute("SELECT user_id FROM users_data WHERE email=%s", (email,))
            if cursor.fetchone():
                conn.close()
                return "Email already registered!"

            # Insert new user into database
            cursor.execute(
                "INSERT INTO users_data (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id",
                (username, email, hashed_pw)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            # Save user info in session
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('home'))
        except Exception as e:
            print("Signup error:", e)
            return f"Signup error: {e}"

    # GET request returns the signup page
    return render_template('signup.html')


# -----------------------------
# Login Route
# -----------------------------
# Handles user login (GET shows form, POST processes login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

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

    # GET request returns the login page
    return render_template('login.html')


# -----------------------------
# Logout Route
# -----------------------------
# Clears the session and logs the user out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# -----------------------------
# Search Route
# -----------------------------
# Handles flight search (GET shows form, POST processes search)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get form data
        trip_type = request.form.get('trip_type', '')
        from_country = request.form.get('from_country', '')
        to_country = request.form.get('to_country', '')
        depart_date = request.form.get('depart_date', '')
        return_date = request.form.get('return_date', '')
        travellers = request.form.get('travellers', '')

        # For debugging: print form input
        print("SEARCH FORM:", trip_type, from_country, to_country, depart_date, return_date, travellers)

        # Return search summary
        return (
            f"Search received: [{trip_type}] "
            f"{from_country} → {to_country}, "
            f"depart: {depart_date}, return: {return_date}, "
            f"travellers: {travellers}"
        )

    # GET request returns the search page
    return render_template('search.html')


# -----------------------------
# Main
# -----------------------------
# Ensure database table exists and start the Flask server
if __name__ == "__main__":
    ensure_users_table()
    app.run(debug=True)
