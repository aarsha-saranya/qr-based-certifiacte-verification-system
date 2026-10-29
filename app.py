<<<<<<< HEAD

import os
import sqlite3
from functools import wraps
from io import BytesIO

import qrcode
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    send_file,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection
from models import get_all_certificates

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "replace-this-with-a-long-random-secret"
)

# --------------------------------------------------
# Authentication helper
# --------------------------------------------------

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    return wrapper


def get_current_user_id():
    user_id = session.get("user_id")
    if user_id is None:
        abort(401)
    return int(user_id)


# --------------------------------------------------
# Home / dashboard
# --------------------------------------------------

@app.route("/")
@login_required
def index():
    user_id = get_current_user_id()

    # This function must filter certificates by owner_user_id.
    certificates = get_all_certificates(owner_user_id=user_id)

    return render_template(
        "index.html",
        certificates=certificates
    )


# --------------------------------------------------
# Signup
# --------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("signup"))

        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    generate_password_hash(password),
                ),
            )
            conn.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("That username or email may already be registered.", "danger")
            return redirect(url_for("signup"))
        finally:
            conn.close()

    return render_template("signup.html")


# --------------------------------------------------
# Login
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        try:
            user = conn.execute(
                """
                SELECT * FROM users
                WHERE lower(email) = ? OR lower(username) = ?
                LIMIT 1
                """,
                (identity, identity),
            ).fetchone()
        finally:
            conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))

        flash("Invalid username/email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


# --------------------------------------------------
# Logout
# --------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------
# Issue a certificate
# --------------------------------------------------

@app.route("/issue", methods=["GET", "POST"])
@login_required
def issue_certificate():
    if request.method == "POST":
        user_id = get_current_user_id()

        # Adjust these field names to match your issue.html form.
        student_name = request.form.get("student_name", "").strip()
        course_name = request.form.get("course_name", "").strip()
        certificate_id = request.form.get("certificate_id", "").strip()

        if not student_name or not course_name or not certificate_id:
            flash("Please complete all certificate fields.", "danger")
            return redirect(url_for("issue_certificate"))

        conn = get_db_connection()
        try:
            # Verify that the ID is not already in use.
            existing = conn.execute(
                "SELECT 1 FROM certificates WHERE certificate_id = ?",
                (certificate_id,),
            ).fetchone()

            if existing:
                flash("That certificate ID already exists.", "danger")
                return redirect(url_for("issue_certificate"))

            # owner_user_id is what separates institutions.
            conn.execute(
                """
                INSERT INTO certificates
                    (certificate_id, student_name, course_name, owner_user_id)
                VALUES (?, ?, ?, ?)
                """,
                (certificate_id, student_name, course_name, user_id),
            )
            conn.commit()

        finally:
            conn.close()

        flash("Certificate issued successfully.", "success")
        return redirect(url_for("index"))

    return render_template("issue.html")


# --------------------------------------------------
# Public certificate verification
# Anyone with a valid certificate ID can verify it.
# --------------------------------------------------

@app.route("/verify", methods=["GET", "POST"])
def verify_certificate():
    certificate = None

    if request.method == "POST":
        certificate_id = request.form.get("certificate_id", "").strip()
        return redirect(
            url_for("verify_certificate_by_id", certificate_id=certificate_id)
        )

    return render_template("verify.html", certificate=certificate)


@app.route("/verify/<certificate_id>")
def verify_certificate_by_id(certificate_id):
    conn = get_db_connection()
    try:
        certificate = conn.execute(
            """
            SELECT certificate_id, student_name, course_name
            FROM certificates
            WHERE certificate_id = ?
            """,
            (certificate_id,),
        ).fetchone()
    finally:
        conn.close()

    return render_template(
        "verify.html",
        certificate=certificate,
        searched=True
    )


# --------------------------------------------------
# QR code generation
# Public QR images only link to public verification.
# --------------------------------------------------

@app.route("/qr/<certificate_id>")
@login_required
def certificate_qr(certificate_id):
    user_id = get_current_user_id()

    conn = get_db_connection()
    try:
        certificate = conn.execute(
            """
            SELECT certificate_id
            FROM certificates
            WHERE certificate_id = ? AND owner_user_id = ?
            """,
            (certificate_id, user_id),
        ).fetchone()
    finally:
        conn.close()

    if not certificate:
        abort(404)

    verify_url = url_for(
        "verify_certificate_by_id",
        certificate_id=certificate_id,
        _external=True,
    )

    qr_image = qrcode.make(verify_url)
    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return send_file(
        image_buffer,
        mimetype="image/png",
        download_name=f"{certificate_id}_qr.png",
    )


# --------------------------------------------------
# Run the application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
=======
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db
from models import add_certificate, get_certificate, get_all_certificates
from certificate_routes import certificate_bp

app = Flask(__name__)
CORS(app)  # allow other origins (e.g. a frontend) to call this API
app.register_blueprint(certificate_bp)
init_db()

REQUIRED_FIELDS = ["name", "email", "course_name", "issued_by", "issue_date"]


@app.route("/")
def home():
    return jsonify({"message": "Certificate backend is running"})


@app.route("/certificates", methods=["POST"])
def create_certificate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        certificate_id = add_certificate(
            name=str(data["name"]).strip(),
            email=str(data["email"]).strip().lower(),
            course_name=str(data["course_name"]).strip(),
            issued_by=str(data["issued_by"]).strip(),
            issue_date=str(data["issue_date"]).strip(),
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"certificate_id": certificate_id}), 201


@app.route("/certificates", methods=["GET"])
def list_certificates():
    return jsonify(get_all_certificates())


@app.route("/certificates/<certificate_id>", methods=["GET"])
def fetch_certificate(certificate_id):
    certificate = get_certificate(certificate_id)
    if certificate is None:
        return jsonify({"error": "Certificate not found"}), 404
    return jsonify(certificate)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed for this URL"}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> 21ecc1c83ddf9d9674b32ef06d00a701d297e60c
