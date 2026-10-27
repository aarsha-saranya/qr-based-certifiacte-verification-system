"""Certificate + QR code generation (ReportLab only, no extra QR library).

Public API
----------
build_verify_url(certificate_id)    -> str
make_qr_drawing(data, size)         -> reportlab Drawing (vector QR code)
qr_svg(data)                        -> str  (QR code as SVG markup)
generate_certificate_pdf(cert)      -> bytes (a landscape A4 PDF)

`cert` is a plain dict (one row from the database). Field names are looked up
through FIELD_ALIASES, so if the backend uses different column names, you only
need to edit that one table.
"""
from __future__ import annotations

import io
import os
from datetime import datetime

from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# Base address of the site. Set VERIFY_BASE_URL when you deploy, e.g.
#   VERIFY_BASE_URL=https://certs.mycollege.edu
BASE_URL = os.environ.get("VERIFY_BASE_URL", "http://localhost:5000")

# Colours
NAVY = colors.HexColor("#1f3a5f")
GOLD = colors.HexColor("#b8923b")
GREY = colors.HexColor("#5b6470")

# Map our logical fields to the column names the backend might use.
FIELD_ALIASES = {
    "id": ("certificate_id", "cert_id", "id"),
    "name": ("student_name", "recipient_name", "name"),
    "course": ("course_name", "course", "title"),
    "date": ("issue_date", "date", "issued_on"),
    "issuer": ("institution", "issuer", "organization"),
}


def _pick(cert: dict, field: str, default: str = "") -> str:
    for key in FIELD_ALIASES[field]:
        value = cert.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def build_verify_url(certificate_id: str, base_url: str | None = None) -> str:
    """The URL stored inside the QR code. Agree on this format with the team."""
    base = (base_url or BASE_URL).rstrip("/")
    return f"{base}/verify/{certificate_id}"


def make_qr_drawing(data: str, size: float = 110) -> Drawing:
    """A square, vector QR code (with its quiet-zone border) of `size` points."""
    widget = qr.QrCodeWidget(data, barLevel="M")  # M = ~15% error correction
    x1, y1, x2, y2 = widget.getBounds()
    w, h = x2 - x1, y2 - y1
    drawing = Drawing(size, size, transform=[size / w, 0, 0, size / h, 0, 0])
    drawing.add(widget)
    return drawing


def qr_svg(data: str, size: float = 300) -> str:
    """The same QR code as SVG text (handy for the web interface)."""
    return renderSVG.drawToString(make_qr_drawing(data, size))


def _fit_font_size(text: str, font: str, max_size: float, max_width: float) -> float:
    """Shrink the font until `text` fits inside max_width."""
    size = max_size
    while size > 12 and stringWidth(text, font, size) > max_width:
        size -= 1
    return size


def _format_date(raw: str) -> str:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt).strftime("%d %B %Y")
        except ValueError:
            continue
    return raw  # already human-readable, or unknown format


def generate_certificate_pdf(cert: dict, base_url: str | None = None) -> bytes:
    """Draw the certificate and return the PDF as bytes."""
    cert_id = _pick(cert, "id")
    if not cert_id:
        raise ValueError("certificate has no id")

    name = _pick(cert, "name", "Recipient Name")
    course = _pick(cert, "course", "Course")
    issued = _format_date(_pick(cert, "date", datetime.now().strftime("%Y-%m-%d")))
    issuer = _pick(cert, "issuer", "Institution")
    verify_url = build_verify_url(cert_id, base_url)

    buffer = io.BytesIO()
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))
    c.setTitle(f"Certificate - {name}")
    c.setAuthor(issuer)
    cx = page_w / 2

    # Double border
    c.setStrokeColor(NAVY)
    c.setLineWidth(4)
    c.rect(24, 24, page_w - 48, page_h - 48)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.rect(36, 36, page_w - 72, page_h - 72)

    # Header
    max_w = page_w - 160
    issuer_size = _fit_font_size(issuer.upper(), "Helvetica", 13, max_w)
    c.setFillColor(GREY)
    c.setFont("Helvetica", issuer_size)
    c.drawCentredString(cx, page_h - 85, issuer.upper())

    c.setFillColor(NAVY)
    c.setFont("Times-Bold", 42)
    c.drawCentredString(cx, page_h - 140, "Certificate of Completion")

    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(cx - 110, page_h - 160, cx + 110, page_h - 160)

    # Body
    c.setFillColor(GREY)
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(cx, page_h - 205, "This is to certify that")

    name_size = _fit_font_size(name, "Times-BoldItalic", 38, max_w)
    c.setFillColor(NAVY)
    c.setFont("Times-BoldItalic", name_size)
    c.drawCentredString(cx, page_h - 255, name)

    c.setFillColor(GREY)
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(cx, page_h - 295, "has successfully completed")

    course_size = _fit_font_size(course, "Helvetica-Bold", 24, max_w)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", course_size)
    c.drawCentredString(cx, page_h - 335, course)

    c.setFillColor(GREY)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, page_h - 370, f"Issued on {issued}")

    # Signature line (bottom left)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.line(80, 105, 250, 105)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 10)
    c.drawCentredString(165, 90, "Authorized Signatory")

    # QR code (bottom right)
    qr_size = 110
    qr_x = page_w - 80 - qr_size
    qr_y = 70
    renderPDF.draw(make_qr_drawing(verify_url, qr_size), c, qr_x, qr_y)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 12, "SCAN TO VERIFY")

    # Certificate ID + URL (bottom centre)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, 62, f"Certificate ID: {cert_id}")
    c.drawCentredString(cx, 50, verify_url)

    c.showPage()
    c.save()
    return buffer.getvalue()