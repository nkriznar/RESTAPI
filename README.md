# 🏨 Hotel Reservation REST API

A production-ready REST API for a Hotel Reservation System, built with **Django** and **Django Rest Framework (DRF)**. The API manages hotels, reservations with UUID-based confirmation numbers, and nested guest data — all backed by a cloud-hosted **Supabase PostgreSQL** database and deployed on **Render**.

> **Course:** MCDA 5550 — Mobile App Development

---

## 🌐 Live API

The API is deployed and publicly accessible at:

| Endpoint | URL |
|----------|-----|
| Hotels List | [https://hotel-reservation-api-8jsa.onrender.com/api/hotels/](https://hotel-reservation-api-8jsa.onrender.com/api/hotels/) |
| Create Reservation | `POST` [https://hotel-reservation-api-8jsa.onrender.com/api/reservations/](https://hotel-reservation-api-8jsa.onrender.com/api/reservations/) |

---

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Framework    | Django 4.2 + Django REST Framework |
| Database     | Supabase (PostgreSQL)             |
| Deployment   | Render                            |
| WSGI Server  | Gunicorn                          |

---

## Project Structure

```
RESTAPI/
├── manage.py
├── requirements.txt
├── .gitignore
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

# 4. Set the DATABASE_URL environment variable
#    (The database is a cloud-hosted Supabase PostgreSQL instance —
#     no local DB setup is required.)
set DATABASE_URL=postgresql://user:password@host:port/dbname     # Windows
# export DATABASE_URL=postgresql://user:password@host:port/dbname  # macOS / Linux

# 5. Run database migrations
python manage.py migrate

# 6. (Optional) Seed sample hotels
python manage.py shell -c "from api.models import Hotel; [Hotel.objects.get_or_create(name=h) for h in ['Marriott', 'Hilton', 'Holiday Inn']]"

# 7. Start the development server
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

## Deployment (Render)

This application is deployed on [Render](https://render.com) as a Web Service.

### How It Works

1. Render connects directly to this GitHub repository.
2. On every push to `main`, Render automatically rebuilds and redeploys.
3. The `DATABASE_URL` environment variable is configured in the Render dashboard to point to the Supabase PostgreSQL instance.

### Build & Start Commands (configured in Render)

| Setting       | Value                                              |
|---------------|----------------------------------------------------|
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput` |
| Start Command | `gunicorn hotel_reservation.wsgi:application`      |

---

## Testing with Postman

1. Import the two endpoints into Postman.
2. **GET** `https://hotel-reservation-api-8jsa.onrender.com/api/hotels/` — verify the hotel list returns.
3. **GET** `https://hotel-reservation-api-8jsa.onrender.com/api/hotels/?checkin=2026-04-01&checkout=2026-04-05` — verify filtering.
4. **POST** `https://hotel-reservation-api-8jsa.onrender.com/api/reservations/` — send the nested JSON body and verify a `201` response with a `confirmation_number`.

---

## License

This project was developed for academic purposes as part of the MCDA 5550 course.
