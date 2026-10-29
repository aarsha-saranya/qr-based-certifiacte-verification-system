# CertiTrust — Certificate Issuing and Verification Website

A responsive Flask + SQLite website with account sign-up/login, certificate issuance, searchable records, PDF downloads and public QR-code verification.

## Run locally on Windows

1. Install Python 3.10+.
2. Open PowerShell in the folder containing `app.py`.
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the website:
   ```powershell
   python app.py
   ```
5. Open `http://127.0.0.1:5000/`. Create an account, then issue a certificate.

## How the workflow works

- Institution user signs up or logs in.
- The dashboard issues a certificate and stores its record in SQLite.
- The site generates a PDF containing a unique QR code.
- Anyone can scan the QR code and visit `/verify/<certificate_id>`; no account is required to verify.
- The verification page queries the stored record and displays its details or a not-found result.
- Dashboard and certificate management API routes require login.

## Test on a mobile phone on the same Wi-Fi

1. Keep `python app.py` running on your computer.
2. Find your computer's local IPv4 address with `ipconfig` in Command Prompt (look for `IPv4 Address`, e.g. `192.168.1.20`).
3. Connect your phone to the same Wi-Fi.
4. On your phone, open `http://192.168.1.20:5000/` using your actual computer IP. Allow Python through Windows Firewall if prompted.
5. QR codes created with the default local configuration still use `localhost`, so for a same-Wi-Fi phone test, stop the server and set the base URL before starting it:
   ```powershell
   $env:VERIFY_BASE_URL="http://192.168.1.20:5000"
   python app.py
   ```
   Replace the IP with your computer's actual IPv4 address. Certificates issued after setting this variable will have phone-reachable QR codes.

## Make it work from any phone, anywhere

A local `127.0.0.1` address is not public. Deploy this app to a hosting provider that supports Python/Flask and HTTPS, then set environment variables:
- `SECRET_KEY`: a long random secret string
- `VERIFY_BASE_URL`: your deployed HTTPS URL, e.g. `https://your-app.onrender.com`
- `COOKIE_SECURE`: `1` when using HTTPS
- `DATABASE_PATH`: path on a persistent disk if the hosting provider uses ephemeral filesystems

Build/start command example:
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`

Use persistent storage for SQLite or migrate to a managed database before relying on the website for real certificates. QR codes already printed with localhost URLs must be reissued to use the public URL.

## Security notes

This is a college-project starter. Set a strong `SECRET_KEY` before deployment, use HTTPS, use persistent database storage, and add institution-level authorization/administration before production use. Public verification intentionally does not require a login.


## Important QR-code note
Set `VERIFY_BASE_URL` before issuing new certificates. QR codes are created at issue time and keep the URL they were generated with. If you deploy later, reissue certificates or generate new PDFs after setting the public HTTPS URL.
