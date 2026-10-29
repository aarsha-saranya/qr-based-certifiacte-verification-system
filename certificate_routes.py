"""Flask blueprint: certificate PDFs, QR images and the issuing page.

Register it in app.py with two lines (after `app = Flask(__name__)`):

    from certificate_routes import certificate_bp
    app.register_blueprint(certificate_bp)

Endpoints
---------
GET /issue                        -> web page: issue a certificate, list, download
GET /certificates/<id>/pdf        -> downloads the PDF
GET /certificates/<id>/preview    -> shows the PDF in the browser tab
GET /certificates/<id>/qr.svg     -> just the QR code image
"""
import io

from flask import Blueprint, Response, abort, jsonify, render_template, send_file

from certificate_pdf import build_verify_url, generate_certificate_pdf, qr_svg
from models import get_certificate

certificate_bp = Blueprint("certificates", __name__, template_folder="templates")


def _load_or_404(certificate_id):
    cert = get_certificate(certificate_id)  # already a dict, or None
    if not cert:
        abort(404, description="Certificate not found")
    return cert


def _pdf_response(certificate_id, as_attachment):
    cert = _load_or_404(certificate_id)
    pdf_bytes = generate_certificate_pdf(cert)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=as_attachment,
        download_name=f"certificate_{certificate_id}.pdf",
    )


@certificate_bp.get("/issue")
def issue_page():

    # Keep the issuing dashboard behind the same login gate as the homepage.
    from flask import redirect
    return redirect("/")

    return render_template("issue.html")



@certificate_bp.get("/certificates/<certificate_id>/pdf")
def download_pdf(certificate_id):
    return _pdf_response(certificate_id, as_attachment=True)


@certificate_bp.get("/certificates/<certificate_id>/preview")
def preview_pdf(certificate_id):
    return _pdf_response(certificate_id, as_attachment=False)


@certificate_bp.get("/certificates/<certificate_id>/qr.svg")
def qr_image(certificate_id):
    _load_or_404(certificate_id)
    return Response(qr_svg(build_verify_url(certificate_id)), mimetype="image/svg+xml")


@certificate_bp.errorhandler(404)
def not_found(err):
    return jsonify(error=str(err.description)), 404