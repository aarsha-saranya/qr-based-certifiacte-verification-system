# CertiTrust: QR-Based Certificate Verification System

A Flask + SQLite website where institutions create an account, issue digital certificates, and give each certificate a unique ID and QR code. Anyone can verify a certificate through a public page, without needing an account.

## Project status

**Completed**

- Sign up, log in and log out for institutions (passwords are stored hashed)
- Dashboard and Issue page for creating certificates (student name, email, course, issuing institution, issue date)
- Unique certificate ID generation (format `CERT-XXXXXXXXXXXX`)
- Records table with search, scoped to the logged-in account (each institution only sees its own certificates)
- QR code for each certificate, shown after issuing (SVG), linking to its verification page
- Public verification page at `/verify/<certificate_id>` showing the student, course, institution, issue date and status, or a "not found" result

**Not finished yet**

- PDF certificate download (the button is on the page but the route is not built yet)
- Scanning the QR code from a phone (see "Known limitations")
- Deployment to a public HTTPS host

## Tech stack

- Python 3.10+
- Flask
- SQLite
- `qrcode` for QR generation
- Plain HTML, CSS and JavaScript for the pages

## Run locally (Windows)

1. Open a terminal in the project folder (the one that contains `app.py`).
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the server:
   ```powershell
   python app.py
   ```
5. Open `http://127.0.0.1:5000/`, create an account, log in, and issue a certificate.

The database file (`certificates.db`) is created automatically on first start.

## Pages and routes

| Method | URL | Access | Purpose |
|---|---|---|---|
| GET | `/` | Login required | Dashboard |
| GET, POST | `/signup` | Public | Create an account |
| GET, POST | `/login` | Public | Log in |
| GET, POST | `/logout` | Public | Log out |
| GET | `/issue` | Login required | Issue page |
| GET | `/certificates` | Login required | List your own certificates (JSON) |
| POST | `/certificates` | Login required | Issue a certificate (JSON) |
| GET | `/certificates/<id>/qr.svg` | Login required, owner only | QR code image |
| GET | `/qr/<id>` | Login required, owner only | QR code image (PNG) |
| GET | `/certificates/<id>` | Public | Certificate details for verification (JSON) |
| GET, POST | `/verify` | Public | Enter a certificate ID |
| GET | `/verify/<id>` | Public | Verification result page |

### Issuing a certificate

`POST /certificates` takes a JSON body with all fields required:

```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "course_name": "Python Workshop",
  "issued_by": "ABC College",
  "issue_date": "2026-10-29"
}
```

Response (201): `{"certificate_id": "CERT-A1B2C3D4E5F6"}`

### Public verification data

`GET /certificates/<id>` returns only what a verifier needs: `certificate_id`, `name`, `course_name`, `issued_by`, `issue_date` and `status`. It does not return the student's email or the issuing account. An unknown ID returns 404 `{"error": "Certificate not found"}`, meaning the certificate is not genuine.

## How verification works

1. The institution issues a certificate. The record is saved in SQLite with the issuing account as its owner.
2. A QR code is generated that links to `/verify/<certificate_id>`.
3. Anyone who opens that link sees the certificate's details, or a "not found" message if the ID does not exist.

## Project structure

```
app.py          Flask app: routes, login, QR generation
database.py     SQLite connection and table creation
models.py       Certificate queries (add, get, list)
templates/      HTML pages (index, login, signup, issue, verify)
static/         verify.css and verify.js for the verification page
requirements.txt
```

## Configuration

Optional environment variables:

- `SECRET_KEY`: secret used to sign login sessions. Set a long random value before any real use.
- `DATABASE_PATH`: custom location for the SQLite file.

## Known limitations

- **QR codes and phones:** a QR code links to the address the site was opened from. A QR created while using `http://127.0.0.1:5000` will not open on a phone, because `127.0.0.1` means the phone itself. Phone scanning needs the site opened through your computer's network address, or a public deployment.
- The app currently runs with Flask's debug server, which is for development only.
- SQLite on a hosting provider with a temporary filesystem can lose data. Use persistent storage before relying on it for real certificates.

## Security notes

This is a college project. Before real use, set a strong `SECRET_KEY`, turn off debug mode, serve over HTTPS, use persistent database storage, and add administrator controls for institutions. The public verification page intentionally does not require a login.