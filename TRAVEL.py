from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from Database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ================== AUTH & HOME ================== #
@app.route("/")
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
            VALUES (%s, %s, %s)
            RETURNING user_id
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
        cur = conn.cursor()

        cur.execute("""
            SELECT user_id, password_hash, username
            FROM users_data
            WHERE email=%s
        """, (email,))
        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            return "Email not found"

        user_id, stored_hash, username = row

        if check_password_hash(stored_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("home"))

        return "Invalid password"

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

    from_city = request.form.get("from_city", "")
    to_city = request.form.get("to_city", "")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ROW_NUMBER() OVER ()        AS flight_id,
            "Airline"                  AS flight_name,
            "Airline"                  AS airline,
            "Source airport"           AS from_airport,
            "Destination airport"      AS to_airport,
            NOW()                      AS departure_time,
            NOW() + interval '2 hour'  AS arrival_time,
            '2h'                       AS duration,
            500                        AS price
        FROM flights
        WHERE
            "Source airport" ILIKE %s
            AND "Destination airport" ILIKE %s
        LIMIT 50;
    """, (f"%{from_city}%", f"%{to_city}%"))

    flights = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("search_results.html", flights=flights)


# ================== PAYMENT ================== #
@app.route("/payment/<int:flight_id>")
def payment(flight_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ROW_NUMBER() OVER ()        AS flight_id,
            "Airline",
            "Source airport",
            "Destination airport",
            500 AS price
        FROM flights
        OFFSET %s LIMIT 1;
    """, (flight_id - 1,))

    flight = cur.fetchone()
    cur.close()
    conn.close()

    if not flight:
        return "Flight not found"

    return render_template("payment.html", flight=flight)

@app.route("/process_payment", methods=["POST"])
def process_payment():
    if "user_id" not in session:
        return jsonify({"success": False}), 401

    data = request.get_json()
    flight_id = data["flight_id"]
    travellers = int(data["travellers"])

    price = 500
    total = price * travellers

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


@app.route("/debug")
def debug():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM flights")
    flights = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"Flights in DB: {flights}"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)