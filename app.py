from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db
from models import add_certificate, get_certificate, get_all_certificates

app = Flask(__name__)
CORS(app)  # allow other origins (e.g. a frontend) to call this API
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