from flask import Flask, request, redirect, url_for, session, render_template, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from psycopg2.extras import RealDictCursor
from Database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# ================== AUTH & HOME ================== #
@app.route("/")
@app.route("/home") 
@app.route("/index")
def home():
    username = session.get("username")
    return render_template("index.html", username=username)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not first_name or not email or not password:
            return "All fields are required!"

        username = f"{first_name} {last_name}".strip()
        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users_data WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return "Email already registered!"

        cur.execute("""
            INSERT INTO users_data (username, email, password_hash)
            VALUES (%s, %s, %s) RETURNING user_id
        """, (username, email, hashed_pw))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        session["user_id"] = user_id
        session["username"] = username
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT user_id, password_hash, username FROM users_data WHERE email=%s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and check_password_hash(row['password_hash'], password):
            session["user_id"] = row['user_id']
            session["username"] = row['username']
            return redirect(url_for("home"))

        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ================== SEARCH ================== #
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    from_val = request.form.get("from_city", "").strip()
    to_val = request.form.get("to_city", "").strip()

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            ROW_NUMBER() OVER () AS flight_id,
            f."Airline" AS airline,
            a1."Name" AS from_airport,
            a1."City" AS from_city,
            a2."Name" AS to_airport,
            a2."City" AS to_city,
            NOW() AS departure_time,
            NOW() + interval '2 hour' AS arrival_time,
            '2h' AS duration,
            500 AS price
        FROM flights f
        JOIN airports a1 ON f."Source airport ID" = a1."Airport ID"::TEXT
        JOIN airports a2 ON f."Destination airport ID" = a2."Airport ID"::TEXT
        WHERE 
            (a1."City" ILIKE %s OR a1."Country" ILIKE %s OR f."Source airport" ILIKE %s)
          AND 
            (a2."City" ILIKE %s OR a2."Country" ILIKE %s OR f."Destination airport" ILIKE %s)
        LIMIT 50;
    """, (f"%{from_val}%", f"%{from_val}%", from_val, 
          f"%{to_val}%", f"%{to_val}%", to_val))

    flights = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("search_results.html", flights=flights)

# ================== PAYMENT ================== #
@app.route("/payment/<int:flight_id>")
def payment_with_flight(flight_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            %s AS flight_id,
            f."Airline" AS airline,
            a1."Name" AS from_airport,
            a1."City" AS from_city,
            a2."Name" AS to_airport,
            a2."City" AS to_city,
            500 AS price
        FROM flights f
        JOIN airports a1 ON f."Source airport ID" = a1."Airport ID"::TEXT
        JOIN airports a2 ON f."Destination airport ID" = a2."Airport ID"::TEXT
        OFFSET %s LIMIT 1;
    """, (flight_id, flight_id - 1))

    flight = cur.fetchone()
    cur.close()
    conn.close()

    if not flight:
        return "Flight not found"

    return render_template("payment.html", flight=flight)

@app.route("/process_payment", methods=["POST"])
def process_payment():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "unauthorized"}), 401

    try:
        data = request.get_json()
        flight_id = data["flight_id"]
        travellers = int(data.get("travellers", 1))
        total = 500 * travellers

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO payments (user_id, flight_id, amount, payment_method, payment_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (session["user_id"], flight_id, total, "Stripe", "Paid"))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "total": total})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

# ================== POST-PAYMENT SUCCESS ROUTES ================== #
@app.route("/success")
@app.route("/confirmation")
@app.route("/done")
@app.route("/payment_success")
@app.route("/complete")
def success_page():
    try:
        return render_template("success.html")
    except:
        return render_template("index.html", message="Thank you! Your payment was successful")

@app.route("/bookings")
@app.route("/my-bookings")
def bookings_page():
    return render_template("index.html", message="Your booking is confirmed!")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)