import requests

response = requests.post(
    "http://127.0.0.1:5000/certificates",
    json={
        "name": "Ravi Kumar",
       
        "course_name": "Flask Bootcamp",
        "issued_by": "ABC College",
        "issue_date": "2026-10-22",
    },
)
print(response.status_code)
print(response.json())