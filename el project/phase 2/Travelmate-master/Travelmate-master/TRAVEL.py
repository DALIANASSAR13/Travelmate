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

# ================== TRAVELLERS ================== #
@app.route("/travellers/<int:flight_id>")
def travellers_with_flight(flight_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get travellers number from query parameters or default to 1
    travellers_num = int(request.args.get("travellers", 1))

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

    return render_template("Travellers.html", flight=flight, travellers_num=travellers_num)

@app.route("/traveller", methods=["POST"])
def save_traveller():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    try:
        # Handle FormData instead of JSON
        travellers_json = request.form.get("travellers")
        if not travellers_json:
            return jsonify({"success": False, "error": "Missing traveller data"}), 400

        travellers = []
        try:
            travellers = eval(travellers_json)  # Since it's passed as string from JavaScript
        except:
            return jsonify({"success": False, "error": "Invalid traveller data format"}), 400

        flight_id = request.form.get("flight_id")
        total_amount = request.form.get("total_amount", 0)

        if not travellers or not flight_id:
            return jsonify({"success": False, "error": "Missing traveller data or flight ID"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Save each traveller
        for traveller in travellers:
            cur.execute("""
                INSERT INTO traveller_data (user_id, full_name, age, passport_number, nationality, gender, email, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session["user_id"],
                traveller.get("full_name"),
                traveller.get("age"),
                traveller.get("passport_number"),
                traveller.get("nationality", "Not Provided"),
                traveller.get("gender", "Not Specified"),
                traveller.get("email", ""),
                traveller.get("phone_number", "Not Provided")
            ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "message": "Traveller details saved successfully"})

    except Exception as e:
        print(f"Error saving traveller: {e}")
        return jsonify({"success": False, "error": "Failed to save traveller details"}), 500

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
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json()

    flight_id = data.get("flight_id")
    payment_method = data.get("payment_method")
    travellers = int(data.get("travellers", 1))

    if not flight_id or not payment_method:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if payment_method.lower() not in ["stripe", "paypal"]:
        return jsonify({"success": False, "message": "Invalid payment method"}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            %s AS flight_id,
            f."Airline" AS airline,
            a1."Name" AS from_airport,
            a2."Name" AS to_airport,
            NOW() AS departure_time,
            NOW() + interval '2 hour' AS arrival_time,
            '2h' AS duration,
            500 AS price,
            'Flight ' || %s AS flight_name
        FROM flights f
        JOIN airports a1 ON f."Source airport ID" = a1."Airport ID"::TEXT
        JOIN airports a2 ON f."Destination airport ID" = a2."Airport ID"::TEXT
        OFFSET %s LIMIT 1;
    """, (flight_id, flight_id, flight_id - 1))

    flight = cur.fetchone()
    if not flight:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Flight not found"}), 404

    total_amount = flight["price"] * travellers
    payment_status = f"Paid via {payment_method.capitalize()}"

    cur.execute("""
        INSERT INTO payments (user_id, flight_id, amount, payment_method, payment_status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING payment_id, created_at
    """, (
        session["user_id"],
        flight_id,
        total_amount,
        payment_method.capitalize(),
        payment_status
    ))

    payment_row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    # ✅ Full ticket summary for frontend
    ticket_summary = {
        "flight_id": flight["flight_id"],
        "airline": flight["airline"],
        "flight_name": flight["flight_name"],
        "from_airport": flight["from_airport"],
        "to_airport": flight["to_airport"],
        "departure_time": str(flight["departure_time"]),
        "arrival_time": str(flight["arrival_time"]),
        "duration": flight["duration"],
        "travellers_number": travellers,
        "price_per_traveller": flight["price"],
        "total_amount": total_amount,
        "payment_method": payment_method.capitalize(),
        "payment_status": payment_status,
        "payment_id": payment_row["payment_id"],
        "payment_created_at": str(payment_row["created_at"])
    }

    return jsonify({"success": True, "ticket_summary": ticket_summary})
    

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

# ==================Ticket-summary- Routes==================#
@app.route("/ticket-summary-page")
def ticket_summary_page():
    return render_template("ticket_summary.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)