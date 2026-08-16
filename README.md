# Hotel Website + AI Assistant (Django + MySQL)

A Django-based hotel website with an integrated AI assistant powered by Google Gemini, running with MySQL in Docker.

## Features

- Hotel landing page with room listing
- AI assistant chat endpoint (`/assistant/chat/`)
- Django admin panel for data management
- MySQL database with Docker Compose
- Ready-to-run local development setup

## Tech Stack

- Python 3.11
- Django
- MySQL 8
- Google Gemini (`google-genai`)
- Docker + Docker Compose

## Project Structure

```text
.
├── manage.py
├── hotel_site/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── hotel/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   └── templates/hotel/index.html
├── service/
│   └── prompt.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 1) Clone from Git

```bash
git clone <your-repository-url>
cd chatbot
```

If your repo name is different, replace `chatbot` with your actual folder name.

---

## 2) Create `.env`

Create a `.env` file in project root:

```env
GEMINI_API_KEY=your_gemini_api_key
MODEL_NAME=models/gemini-2.5-flash
DJANGO_SECRET_KEY=change-this-secret
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=*
```

Notes:
- `GEMINI_API_KEY` is required for AI assistant responses.
- `DJANGO_DEBUG=1` is for development only.

---

## 3) Run with Docker (recommended)

```bash
docker compose up --build
```

Open in browser:
- `http://localhost:8000` (Hotel website)
- `http://localhost:8000/admin/` (Django admin)

Run in background:

```bash
docker compose up --build -d
```

Stop:

```bash
docker compose down
```

Reset containers + DB volume:

```bash
docker compose down -v
```

---

## 4) Create Django Admin User

```bash
docker compose exec web python manage.py createsuperuser
```

Then login at `http://localhost:8000/admin/`.

---

## 5) Add Rooms to Database

### Option A: Django Admin
- Go to `/admin/`
- Add `Room` records

### Option B: Django Shell

```bash
docker compose exec web python manage.py shell
```

```python
from hotel.models import Room
Room.objects.create(room_number="101", room_type="Deluxe Suite", price_per_night=180, is_available=True)
Room.objects.create(room_number="102", room_type="Family Room", price_per_night=140, is_available=True)
Room.objects.create(room_number="103", room_type="Standard Room", price_per_night=95, is_available=True)
exit()
```

---

## 6) API Endpoints

### `GET /`
Hotel homepage.

### `POST /assistant/chat/`
AI assistant endpoint.

Request:

```json
{
  "message": "Do you have sea view rooms?"
}
```

Response:

```json
{
  "response": "Yes, Deluxe Suite offers sea view and breakfast included."
}
```

### `GET /admin/`
Django admin dashboard.

---

## 7) Open MySQL Database

### Inside container

```bash
docker compose exec mysql mysql -uroot -p
```

Password: `root_password`

Then:

```sql
USE hotel_db;
SHOW TABLES;
```

### From host machine

```bash
mysql -h 127.0.0.1 -P 3307 -u hotel_user -p hotel_db
```

Password: `hotel_pass`

---

## 8) Run Without Docker (optional)

Requirements:
- Python 3.11+
- MySQL running locally

Steps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set DB env values for your local MySQL and run:

```bash
python manage.py migrate
python manage.py runserver
```

---

## 9) Troubleshooting

### MySQL connection error (`Can't connect to MySQL server on 'mysql'`)

Use:

```bash
docker compose down
docker compose up --build
```

If needed:

```bash
docker compose down -v
docker compose up --build
```

### Gemini API key error

Check `.env` has a valid `GEMINI_API_KEY`.

### Port already in use

If `8000` or `3307` is occupied, change ports in `docker-compose.yml`.

---

## 10) Useful Commands

```bash
# View logs
docker compose logs -f

# Web logs only
docker compose logs -f web

# MySQL logs only
docker compose logs -f mysql

# Run migrations manually
docker compose exec web python manage.py migrate

# Open Django shell
docker compose exec web python manage.py shell
```

---

## Production Notes

Before production:
- set `DJANGO_DEBUG=0`
- use a strong `DJANGO_SECRET_KEY`
- configure strict `DJANGO_ALLOWED_HOSTS`
- serve Django with Gunicorn/Uvicorn + reverse proxy
- secure DB credentials and network

---

## AI Room Reservation

The assistant can now create reservations directly from chat using database data.

### Example booking message

```text
Book room 101 for John Doe on 2026-05-10 for 2 nights
```

### Required booking fields in message

- room number (example: `room 101`)
- guest name (example: `for John Doe` or `name is John Doe`)
- check-in date in `YYYY-MM-DD`
- nights (optional, default is `1`)

When booking succeeds:
- a `Reservation` record is created
- selected room is marked unavailable (`is_available=False`)

If data is missing, assistant asks for missing fields.ssss

