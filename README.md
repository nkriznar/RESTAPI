# 🏨 Hotel Reservation REST API

A production-ready REST API for a Hotel Reservation System, built with **Django** and **Django Rest Framework (DRF)**. The API manages hotels, reservations with UUID-based confirmation numbers, and nested guest data — all backed by a cloud-hosted **Supabase PostgreSQL** database and deployed on **AWS Elastic Beanstalk**.

> **Course:** MCDA 5550 — Mobile App Development

---

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Framework    | Django 4.2 + Django REST Framework |
| Database     | Supabase (PostgreSQL)             |
| Deployment   | AWS Elastic Beanstalk             |
| WSGI Server  | Gunicorn                          |

---

## Project Structure

```
RESTAPI/
├── manage.py
├── requirements.txt
├── .gitignore
├── .ebextensions/
│   └── django.config          # AWS EB configuration
├── hotel_reservation/         # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── api/                       # Core application
    ├── models.py              # Hotel, Reservation, Guest
    ├── serializers.py         # Nested serializer with custom create()
    ├── views.py               # ListAPIView, CreateAPIView
    ├── urls.py
    └── admin.py
```

---

## Local Setup

### Prerequisites

- Python 3.10+
- pip
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/nkriznar/RESTAPI.git
cd RESTAPI

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
#    (The database is a cloud-hosted Supabase PostgreSQL instance —
#     no local DB setup is required.)
python manage.py migrate

# 5. (Optional) Seed sample hotels
python manage.py shell -c "from api.models import Hotel; [Hotel.objects.get_or_create(name=h) for h in ['Marriott', 'Hilton', 'Holiday Inn']]"

# 6. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## API Endpoints

### `GET /api/hotels/`

Returns a list of available hotels. Optionally accepts `checkin` and `checkout` query parameters to **filter out** hotels that already have a reservation overlapping the requested date range.

**Request (all hotels):**
```
GET /api/hotels/
```

**Request (filtered by availability):**
```
GET /api/hotels/?checkin=2026-04-01&checkout=2026-04-05
```

**Response — `200 OK`:**
```json
[
    { "id": 1, "name": "Marriott" },
    { "id": 2, "name": "Hilton" },
    { "id": 3, "name": "Holiday Inn" }
]
```

> Hotels with existing reservations that overlap the provided date range are excluded from the results.

---

### `POST /api/reservations/`

Creates a new reservation with a nested list of guests. Returns a system-generated UUID confirmation number.

**Request Body:**
```json
{
    "hotel_name": "Marriott",
    "checkin": "2026-04-01",
    "checkout": "2026-04-05",
    "guests_list": [
        { "guest_name": "John Doe", "gender": "Male" },
        { "guest_name": "Jane Doe", "gender": "Female" }
    ]
}
```

**Response — `201 Created`:**
```json
{
    "confirmation_number": "a7f3b2c1-8d4e-4f5a-9b6c-1234567890ab"
}
```

**Error Response — `400 Bad Request` (checkout before checkin):**
```json
{
    "non_field_errors": ["checkout date must be after checkin date."]
}
```

---

## Database Schema

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    Hotel     │       │   Reservation    │       │    Guest     │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)          │  1──▶ │ id (PK)      │
│ name (unique)│       │ hotel_name       │  N    │ reservation  │
│              │       │ checkin          │◀──────│  (FK)        │
│              │       │ checkout         │       │ guest_name   │
│              │       │ confirmation_    │       │ gender       │
│              │       │   number (UUID)  │       │              │
└──────────────┘       └──────────────────┘       └──────────────┘
```

---

## AWS Elastic Beanstalk Deployment

### Prerequisites

- AWS CLI configured (`aws configure`)
- EB CLI installed (`pip install awsebcli`)

### Deployment Steps

```bash
# 1. Initialize Elastic Beanstalk
eb init -p python-3.11 hotel-reservation-api --region us-east-1

# 2. Create an environment and deploy
eb create hotel-reservation-env

# 3. Open the deployed application
eb open

# 4. (Subsequent deployments)
eb deploy
```

The `.ebextensions/django.config` file automatically handles:
- Setting the WSGI path to `hotel_reservation.wsgi:application`
- Running `python manage.py migrate` on each deploy
- Collecting static files

### Useful EB Commands

| Command       | Description                    |
|---------------|--------------------------------|
| `eb status`   | Check environment health       |
| `eb logs`     | View application logs          |
| `eb ssh`      | SSH into the EC2 instance      |
| `eb terminate`| Tear down the environment      |

---

## Testing with Postman

1. Import the two endpoints into Postman.
2. **GET** `http://<your-eb-url>/api/hotels/` — verify the hotel list returns.
3. **GET** `http://<your-eb-url>/api/hotels/?checkin=2026-04-01&checkout=2026-04-05` — verify filtering.
4. **POST** `http://<your-eb-url>/api/reservations/` — send the nested JSON body and verify a `201` response with a `confirmation_number`.

---

## License

This project was developed for academic purposes as part of the MCDA 5550 course.
