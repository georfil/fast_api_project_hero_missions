# Hero Missions API

A RESTful API for managing **heroes** and their **missions**, built with FastAPI, SQLModel, and JWT authentication. Users can register, log in, and perform full CRUD operations on heroes and missions — with admin-gated deletion and business logic that prevents removing heroes mid-mission.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [How to Run](#3-how-to-run)
4. [API Endpoints](#4-api-endpoints)
5. [Swagger UI](#5-swagger-ui)
6. [Strengths & Future Improvements](#6-strengths--future-improvements)

---

## 1. Project Overview

| | |
|---|---|
| **Framework** | FastAPI 0.136.1 |
| **ORM** | SQLModel (SQLAlchemy + Pydantic) |
| **Database** | SQLite (`hero_missions.db`) |
| **Auth** | JWT Bearer tokens (HS256, 30-min expiry) |
| **Password hashing** | bcrypt via passlib |
| **Testing** | pytest + in-memory SQLite |

### Core Concepts

- **Heroes** have a name, power, level (1–100), and an active status.
- **Missions** have a title, difficulty (1–10), a completion flag, and belong to a hero.
- **Users** register and log in to interact with the write endpoints. Deletion endpoints are admin-only.
- A hero **cannot be deleted** while they have uncompleted missions — the API returns `409 Conflict`.

---

## 2. Project Structure

```
fast_api_project_hero_missions/
├── app/
│   ├── __init__.py
│   ├── main.py              # App factory, lifespan, router registration
│   ├── models.py            # SQLModel tables + Pydantic request/response schemas
│   ├── dependencies.py      # JWT auth dependencies (CurrentUser, AdminUser)
│   ├── security.py          # Password hashing & JWT creation
│   ├── db.py                # SQLite engine setup & session dependency
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /auth  — register, login, me
│       ├── heroes.py        # /heroes — hero CRUD
│       └── missions.py      # /missions — mission CRUD
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py      # Fixtures: in-memory DB, mock users, TestClient
│       ├── test_auth.py     # 6 auth tests
│       ├── test_heroes.py   # 11 hero tests
│       └── test_missions.py # 10 mission tests
├── requirements.txt
└── README.md
```

---

## 3. How to Run

### Prerequisites

```bash
pip install -r requirements.txt
```

### Start the development server

```bash
cd app
fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`.

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive) |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation |

### Run the tests

```bash
# All tests
pytest

# Specific test modules
pytest app/tests/test_auth.py
pytest app/tests/test_heroes.py
pytest app/tests/test_missions.py

# Verbose output
pytest -v
```

Tests run against an **in-memory SQLite database** — no side effects on your development DB.

---

## 4. API Endpoints

### Authentication — `/auth`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | — | Register a new user |
| `POST` | `/auth/login` | — | Log in and receive a JWT token (OAuth2 form data) |
| `GET` | `/auth/me` | Bearer token | Get the current user's profile |

**Register request body**
```json
{ "username": "string", "password": "string" }
```

**Login** uses `application/x-www-form-urlencoded` (standard OAuth2 password flow):
```
username=...&password=...
```

**Login response**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

### Heroes — `/heroes`

| Method | Path | Auth | Description | Notable errors |
|--------|------|------|-------------|----------------|
| `GET` | `/heroes` | — | List all heroes | — |
| `GET` | `/heroes/{hero_id}` | — | Get a single hero | `404` |
| `POST` | `/heroes` | Bearer token | Create a hero | — |
| `PATCH` | `/heroes/{hero_id}` | Bearer token | Partially update a hero | `404` |
| `DELETE` | `/heroes/{hero_id}` | Admin token | Delete a hero | `404`, `409` if active missions exist |

**Create / update schema**
```json
{
  "name": "string (min 3)",
  "power": "string (min 3)",
  "level": 1,
  "active": true
}
```
All fields are optional for `PATCH`.

---

### Missions — `/missions`

| Method | Path | Auth | Description | Notable errors |
|--------|------|------|-------------|----------------|
| `GET` | `/missions` | — | List all missions | — |
| `GET` | `/missions/{mission_id}` | — | Get a single mission | `404` |
| `POST` | `/missions` | Bearer token | Create a mission | `409` if `hero_id` doesn't exist |
| `PATCH` | `/missions/{mission_id}` | Bearer token | Partially update a mission | `404` |
| `DELETE` | `/missions/{mission_id}` | Admin token | Delete a mission | `404` |

**Create / update schema**
```json
{
  "title": "string (min 5)",
  "difficulty": 5,
  "completed": false,
  "hero_id": 1
}
```
All fields are optional for `PATCH`.

---

### Error reference

| Code | Meaning |
|------|---------|
| `400` | Duplicate username on registration |
| `401` | Missing, invalid, or expired JWT |
| `403` | Valid token but not an admin |
| `404` | Hero or mission not found |
| `409` | Hero has active missions (delete) / hero not found (mission create) |

---

## 5. Swagger UI

<!-- TODO: Replace this placeholder with a screenshot of the Swagger UI -->
> **Screenshot coming soon.** Start the server with `uvicorn app.main:app --reload`, open `http://127.0.0.1:8000/docs`, and place your screenshot here.

---

## 6. Strengths & Future Improvements

### Strengths

- **Clean separation of concerns** — routers, models, dependencies, and security each live in their own module, making the codebase easy to navigate and extend.
- **Input validation at the schema level** — `StrictModel` with `extra="forbid"` rejects unknown fields early, and field constraints (min lengths, numeric ranges) are enforced by Pydantic before any DB interaction.
- **Role-based access control** — the `CurrentUser` / `AdminUser` dependency pair keeps auth logic out of route handlers cleanly.
- **Business logic integrity** — the `409 Conflict` guard on hero deletion ensures you can never orphan active missions accidentally.
- **Comprehensive test suite** — 27 tests covering happy paths, 404s, 409s, and auth failures, all running against an isolated in-memory database so there are zero side effects.
- **Automatic DB setup** — the lifespan event creates all tables on startup, so there's no migration step needed for a fresh environment.

### Future Improvements

- **Environment-based secrets** — the JWT secret key is currently hardcoded as `"demo"`. Moving it to an environment variable (e.g. via `python-dotenv`) is the first step toward production readiness.
- **Pagination** — `GET /heroes` and `GET /missions` return the full table. Adding `offset` / `limit` query parameters would be straightforward with SQLModel and prevent issues at scale.
- **Refresh tokens** — 30-minute access tokens are short-lived and secure, but there's no refresh flow. Adding a long-lived refresh token endpoint would improve usability without sacrificing security.
- **Soft deletes** — rather than hard-deleting records, adding an `is_deleted` flag would preserve historical data and make the `409` logic for heroes even more nuanced.
- **Mission assignment rules** — currently any authenticated user can assign any mission to any hero. A more sophisticated system might limit assignments based on hero level or active mission count.
- **Password strength validation** — registration accepts any password. Adding minimum length and complexity rules via a Pydantic validator would improve security.
- **Async database sessions** — swapping the synchronous SQLModel session for an async one (`AsyncSession`) would let FastAPI fully leverage its async runtime under load.
