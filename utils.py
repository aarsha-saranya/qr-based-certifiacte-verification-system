import secrets
import string
from datetime import datetime

ALPHABET = string.ascii_uppercase + string.digits


def generate_certificate_id():
    year = datetime.now().year
    random_part = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return f"CERT-{year}-{random_part}"


if __name__ == "__main__":
    for _ in range(5):
        print(generate_certificate_id())