from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os

# نستورد من Database.py
from .Database import get_db_connection, init_db

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
        if not conn:
            return "Database connection failed"
        cur = conn.cursor()

        # نتأكد إن الإيميل مش موجود قبل كده
        cur.execute("SELECT user_id FROM users_data WHERE email=%s", (email,))
        if cur.fetchone():
            conn.close()
            return "Email already registered!"

        cur.execute("""
            INSERT INTO users_data (username, email, password_hash)
            VALUES (%s,%s,%s) RETURNING user_id
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

        if not email or not password:
            return "Email and password are required!"

        conn = get_db_connection()
        if not conn:
            return "Database connection failed"

        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash, username FROM users_data WHERE email=%s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return "Email not found. Please signup first."

        user_id, stored_hash, username = row

        if check_password_hash(stored_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid email or password."

    return render_template("login.html")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cur = conn.cursor()
    cur.execute("SELECT email, username FROM users_data WHERE user_id=%s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("profile.html", user=user_data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ================== SEARCH & RESULTS ================== #

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')

    from_city = request.form.get('from_city', '').strip()
    to_city = request.form.get('to_city', '').strip()
    depart_date = request.form.get('depart_date', '').strip()
    return_date = request.form.get('return_date', '').strip()
    travellers = request.form.get('travellers', '').strip()
    trip_type = request.form.get('trip_type', '').strip()
    flight_class = request.form.get('flight_class', '').strip()

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    try:
        cur = conn.cursor()
        query = """
            SELECT
                f.flight_id,
                f.flight_name,
                f.airline,
                f.from_airport,
                f.to_airport,
                f.departure_time,
                f.arrival_time,
                f.duration,
                f.price,
                af.city AS from_city,
                af.country AS from_country,
                at.city AS to_city,
                at.country AS to_country
            FROM flights f
            LEFT JOIN airports af ON f.from_airport = af.iata
            LEFT JOIN airports at ON f.to_airport = at.iata
            WHERE
              (
                f.from_airport ILIKE %s
                OR af.city ILIKE %s
                OR af.country ILIKE %s
              )
              AND
              (
                f.to_airport ILIKE %s
                OR at.city ILIKE %s
                OR at.country ILIKE %s
              )
            LIMIT 50;
        """
        from_pattern = f"%{from_city}%"
        to_pattern = f"%{to_city}%"

        cur.execute(
            query,
            (
                from_pattern, from_pattern, from_pattern,
                to_pattern, to_pattern, to_pattern
            )
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        flights = []
        for r in rows:
            flights.append({
                "flight_id": r[0],
                "flight_name": r[1],
                "airline": r[2],
                "from_airport": r[3],
                "to_airport": r[4],
                "departure_time": r[5],
                "arrival_time": r[6],
                "duration": r[7],
                "price": float(r[8]),
                "from_city": r[9],
                "from_country": r[10],
                "to_city": r[11],
                "to_country": r[12],
            })

        # نخزن معلومات البحث في الـ session عشان نستخدمها في صفحة الدفع
        session['search_info'] = {
            "from_city": from_city,
            "to_city": to_city,
            "depart_date": depart_date,
            "return_date": return_date,
            "travellers": travellers,
            "trip_type": trip_type,
            "flight_class": flight_class,
        }

        return render_template(
            'search_results.html',
            flights=flights,
            search_info=session['search_info']
        )

    except Exception as e:
        print("Search error:", e)
        return f"Search error: {e}"


# ================== PAYMENT PAGES ================== #

# لو حد فتح /payment بس → رجّعه على صفحة البحث
@app.route("/payment", methods=["GET"])
def payment():
    return redirect(url_for("search"))


@app.route("/ticket-summary-page")
def ticket_summary_page():
    # بس بيرندر الـ HTML – الداتا هتيجي بالـ JS من sessionStorage
    return render_template("ticket_summary.html")


@app.route("/payment/<int:flight_id>", methods=["GET"])
def payment_with_flight(flight_id):
    # لازم يكون عامل Login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # نجيب search_info من الـ session (جاية من صفحة الـ search)
    search_info = session.get("search_info", {})

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cur = conn.cursor()
    cur.execute("""
        SELECT
            flight_id,
            flight_name,
            airline,
            from_airport,
            to_airport,
            departure_time,
            arrival_time,
            duration,
            price
        FROM flights
        WHERE flight_id = %s
    """, (flight_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return "Flight not found", 404

    flight = {
        "flight_id": row[0],
        "flight_name": row[1],
        "airline": row[2],
        "from_airport": row[3],
        "to_airport": row[4],
        "departure_time": row[5],
        "arrival_time": row[6],
        "duration": row[7],
        "price": float(row[8]),
    }

    return render_template(
        "payment.html",
        flight=flight,
        search_info=search_info
    )


# ================== PROCESS PAYMENT API ================== #

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # نتأكد إن اليوزر داخل بحسابه
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "You must be logged in to pay."}), 401

    data = request.get_json()

    flight_id = data.get("flight_id")
    payment_method = data.get("payment_method")
    travellers_number = data.get("travellers_number")

    if not flight_id or not payment_method or not travellers_number:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        travellers_number = int(travellers_number)
        if travellers_number <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"success": False, "message": "Invalid travellers number"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cur = conn.cursor()
    # نجيب بيانات الرحلة
    cur.execute("""
        SELECT
            flight_id,
            flight_name,
            airline,
            from_airport,
            to_airport,
            departure_time,
            arrival_time,
            duration,
            price
        FROM flights
        WHERE flight_id = %s
    """, (flight_id,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Flight not found"}), 404

    flight = {
        "flight_id": row[0],
        "flight_name": row[1],
        "airline": row[2],
        "from_airport": row[3],
        "to_airport": row[4],
        "departure_time": row[5],
        "arrival_time": row[6],
        "duration": row[7],
        "price": float(row[8]),
    }

    total_amount = flight["price"] * travellers_number

    if payment_method.lower() not in ["paypal", "stripe"]:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Invalid payment method"}), 400

    payment_status = f"paid via {payment_method.capitalize()}"

    # ندخل الـ payment في الجدول
    cur.execute("""
        INSERT INTO payments (user_id, flight_id, amount, payment_method, payment_status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING payment_id, created_at
    """, (
        user_id,
        flight["flight_id"],
        total_amount,
        payment_method.capitalize(),
        payment_status
    ))
    payment_row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    # نجهّز الداتا اللي هنستخدمها في صفحة الملخص
    ticket_summary = {
        "flight_id": flight["flight_id"],
        "flight_name": flight["flight_name"],
        "airline": flight["airline"],
        "from_airport": flight["from_airport"],
        "to_airport": flight["to_airport"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "duration": flight["duration"],
        "price_per_traveller": flight["price"],
        "travellers_number": travellers_number,
        "total_amount": float(total_amount),
        "payment_method": payment_method,
        "payment_status": payment_status,
        "payment_id": payment_row[0],
        "payment_created_at": str(payment_row[1]),
    }

    return jsonify({"success": True, "ticket_summary": ticket_summary})


# ================== DEBUG ROUTES ================== #

@app.route("/debug-flights")
def debug_flights():
    conn = get_db_connection()
    if not conn:
        return "DB error"

    cur = conn.cursor()
    cur.execute("""
        SELECT flight_id, flight_name, airline, from_airport, to_airport, price
        FROM flights
        LIMIT 20;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    html = "<h3>Sample flights from DB</h3><ul>"
    for r in rows:
        html += f"<li>#{r[0]} - {r[1]} ({r[2]}): {r[3]} ➜ {r[4]} — ${float(r[5])}</li>"
    html += "</ul>"
    return html


@app.route("/debug")
def debug():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM airports;")
    airports_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM flights;")
    flights_count = c.fetchone()[0]

    conn.close()
    return f"Airports: {airports_count} — Flights: {flights_count}"


# ================== APP ENTRY ================== #

if __name__ == "__main__":
    # نعمل الجداول + seeding من Database.py
    init_db(seed_data=True)
    app.run(debug=True)
