from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --------------------------------------------------
# إنشاء التطبيق — مهم جدًا static_folder = '.' عشان يقدم try.html
# --------------------------------------------------
app = Flask(__name__, static_folder='.', static_url_path='')

# مفتاح السيشن
app.config["SECRET_KEY"] = "change_this_to_a_strong_secret"

# قاعدة البيانات SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cloudtrip.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# تفعيل CORS للـAPI
CORS(app, supports_credentials=True)

# DB
db = SQLAlchemy(app)


# --------------------------------------------------
# موديل المستخدم
# --------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
        }


# --------------------------------------------------
# Helper لمعرفة المستخدم الحالي من السيشن
# --------------------------------------------------
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


# --------------------------------------------------
# Route رئيسي — يقدم صفحة try.html
# --------------------------------------------------
@app.route("/")
def home():
    # يقدم الصفحة الأساسية
    return send_from_directory(".", "try.html")


# --------------------------------------------------
# SIGN UP API
# --------------------------------------------------
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not first_name or not last_name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered."}), 409

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id

    return jsonify({"success": True, "user": user.to_dict()}), 201


# --------------------------------------------------
# LOGIN API
# --------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session["user_id"] = user.id

    return jsonify({"success": True, "user": user.to_dict()}), 200


# --------------------------------------------------
# LOGOUT API
# --------------------------------------------------
@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"success": True}), 200


# --------------------------------------------------
# CHECK LOGGED IN
# --------------------------------------------------
@app.route("/api/auth/me", methods=["GET"])
def me():
    user = current_user()
    if not user:
        return jsonify({"authenticated": False}), 200

    return jsonify({
        "authenticated": True,
        "user": user.to_dict()
    }), 200


# --------------------------------------------------
# تشغيل السيرفر
# --------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
