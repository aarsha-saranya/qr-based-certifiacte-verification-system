# Certificate Management Backend

Flask + SQLite backend that stores and serves certificate records.

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Server runs at http://127.0.0.1:5000. The database is created automatically.

## API

| Method | URL | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/certificates` | Create a certificate |
| GET | `/certificates` | List all certificates |
| GET | `/certificates/<certificate_id>` | Get one certificate |

### POST /certificates

Request body (JSON, all fields required):

```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "course_name": "Python Workshop",
  "issued_by": "ABC College",
  "issue_date": "2026-10-22"
}
```

Response (201): `{"certificate_id": "CERT-2026-K2M9X4TB"}`

### GET /certificates/<certificate_id>

Returns the record, or 404 `{"error": "Certificate not found"}`
if the ID does not exist (meaning the certificate is not genuine).

## Testing

With the server running, in a second terminal: `python test_api.py`"# qr-based-certifiacte-verification-system" 
