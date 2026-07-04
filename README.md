# bbl — Booking API

A booking REST API built with FastAPI and SQLAlchemy, with JWT-based authentication. Data is stored in a local SQLite database (`database.db`), created automatically on first run.

## Requirements

- Python 3.10+

## Setup

1. Clone the repo and create a virtual environment:

   ```bash
   git clone https://github.com/newbieeiei1234/bbl.git
   cd bbl
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with a secret key for signing JWTs:

   ```bash
   echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
   ```

## Run the server

```bash
uvicorn main:app --reload
```

The API is now available at http://localhost:8000, with interactive docs at http://localhost:8000/docs.

## API endpoints

| Method | Path            | Auth      | Description                       |
| ------ | --------------- | --------- | --------------------------------- |
| POST   | `/register`     | —         | Register a new user               |
| POST   | `/login`        | —         | Log in, returns a JWT (expires in 30 min) |
| GET    | `/bookings/all` | Bearer    | List the current user's bookings  |
| POST   | `/bookings/new` | Bearer    | Create a new booking              |
| PUT    | `/bookings`     | Bearer    | Edit an existing booking          |

Authenticated endpoints expect an `Authorization: Bearer <token>` header using the token returned by `/login`.

## Run the tests

```bash
pytest
```

Tests run against a temporary SQLite database, so they won't touch `database.db`.

## Project structure

```
├── main.py            # FastAPI app entry point
├── api/
│   ├── auth/          # Register/login routes, JWT utilities
│   └── booking/       # Booking routes
├── db/
│   ├── db_connection.py
│   └── models/        # SQLAlchemy models (users, bookings)
└── tests/             # pytest test suite
```
