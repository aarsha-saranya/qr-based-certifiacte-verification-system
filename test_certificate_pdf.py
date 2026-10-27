"""Tests for the PDF/QR part. No server needed.

Run with:  python test_certificate_pdf.py
"""
from certificate_pdf import build_verify_url, generate_certificate_pdf, qr_svg

# Same shape as the dict returned by models.get_certificate()
SAMPLE = {
    "certificate_id": "CERT-2026-K2M9X4TB",
    "name": "Asha Rao",
    "email": "asha@example.com",
    "course_name": "Python Workshop",
    "issued_by": "ABC College",
    "issue_date": "2026-10-22",
    "created_at": "2026-10-22 10:00:00",
}


def test_verify_url_format():
    url = build_verify_url("CERT-2026-K2M9X4TB", base_url="https://example.edu/")
    assert url == "https://example.edu/verify/CERT-2026-K2M9X4TB"


def test_pdf_is_generated():
    pdf = generate_certificate_pdf(SAMPLE)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 2000


def test_long_values_do_not_crash():
    long = dict(SAMPLE, name="A Very Long Recipient Name " * 4,
                course_name="An Extremely Long Course Title " * 4)
    assert generate_certificate_pdf(long).startswith(b"%PDF")


def test_missing_id_is_rejected():
    try:
        generate_certificate_pdf({"name": "No Id"})
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_qr_svg_is_svg():
    assert "<svg" in qr_svg("https://example.edu/verify/1")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
    with open("sample_certificate.pdf", "wb") as f:
        f.write(generate_certificate_pdf(SAMPLE))
    print("Wrote sample_certificate.pdf")