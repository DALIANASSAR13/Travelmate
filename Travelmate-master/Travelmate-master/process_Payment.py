from flask import Blueprint, request, jsonify
from Database import get_db_connection

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/process_payment', methods=["POST"])
def process_payment():
    data = request.json 

    flight_name = data.get("flight_name")
    payment_method = data.get("payment_method")
    total_amount = data.get("total_amount")
    user_id = data.get("user_id")

    if not flight_name or not payment_method or not total_amount or not user_id:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT flight_id, flight_name, airline, from_airport, to_airport, departure_time, arrival_time, duration, price
        FROM flights
        WHERE flight_name = %s
    """, (flight_name,))
    flight_row = cur.fetchone()

    if not flight_row:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Flight not found"}), 404

    flight = {
        "flight_id": flight_row[0],
        "flight_name": flight_row[1],
        "airline": flight_row[2],
        "from": flight_row[3],
        "to": flight_row[4],
        "departure_time": flight_row[5],
        "arrival_time": flight_row[6],
        "duration": flight_row[7],
        "price": float(flight_row[8])
    }

    if total_amount != flight["price"]:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Amount does not match flight price"}), 400

    if payment_method.lower() not in ["paypal", "stripe"]:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Invalid payment method"}), 400

    if payment_method.lower() == "paypal":
        payment_status = "paid via PayPal"
    else:
        payment_status = "paid via Stripe"

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

    ticket_summary = {
        "flight": flight,
        "payment_status": payment_status,
        "payment_id": payment_row[0],
        "payment_created_at": str(payment_row[1])
    }

    return jsonify({"success": True, "ticket_summary": ticket_summary})