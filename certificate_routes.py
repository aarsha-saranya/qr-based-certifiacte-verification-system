
"""Certificate PDF download and preview routes."""

from io import BytesIO

from flask import (
    Blueprint,
    abort,
    redirect,
    send_file,
    session,
    url_for,
)

from certificate_pdf import generate_certificate_pdf
from models import get_certificate


certificate_bp = Blueprint("certificates", __name__)


def _get_owned_certificate(certificate_id):
    """Return a certificate only to its issuing account."""
    user_id = session.get("user_id")

    if user_id is None:
        return None

    certificate = get_certificate(certificate_id)

    if not certificate:
        return None

    if certificate.get("owner_user_id") != int(user_id):
        return None

    return certificate


def _make_pdf_response(certificate_id, as_attachment):
    certificate = _get_owned_certificate(certificate_id)

    if certificate is None:
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        abort(404, description="Certificate not found")

    pdf_bytes = generate_certificate_pdf(certificate)

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=as_attachment,
        download_name=f"certificate_{certificate_id}.pdf",
    )


@certificate_bp.route(
    "/certificates/<certificate_id>/pdf",
    methods=["GET"],
)
def download_pdf(certificate_id):
    """Download a generated certificate PDF."""
    return _make_pdf_response(
        certificate_id,
        as_attachment=True,
    )


@certificate_bp.route(
    "/certificates/<certificate_id>/preview",
    methods=["GET"],
)
def preview_pdf(certificate_id):
    """Display a generated certificate PDF in the browser."""
    return _make_pdf_response(
        certificate_id,
        as_attachment=False,
    )
