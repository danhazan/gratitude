# Grateful Project: Architecture & Setup Guide

## Overview

This project is a modern web application with a FastAPI backend, a Next.js frontend, and a PostgreSQL database. All authentication and business logic are handled by the backend; the frontend acts as a proxy for user and authentication requests.

---

## Architecture

- **Backend:** FastAPI (Python, SQLAlchemy, JWT)
  - Location: `apps/api`
  - Handles all business logic, authentication, and database access
- **Frontend:** Next.js (React, TypeScript)
  - Location: `apps/web`
  - Proxies authentication and user-related requests to the backend
- **Database:** PostgreSQL
  - Used by the backend for persistent storage

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+
- PostgreSQL 14+

---

## 1. Clone the Repository

```sh
git clone <repo-url>
cd grateful
```

---

## 2. Database Setup

1. Install PostgreSQL and ensure it is running.
2. Create a database and user:
   ```sh
   psql -U postgres
   CREATE DATABASE grateful;
   CREATE USER grateful WITH PASSWORD 'iamgreatful';
   GRANT ALL PRIVILEGES ON DATABASE grateful TO grateful;
   \q
   ```
3. (Optional) Update credentials in `.env` files if you use different values.

---

## 3. Backend (FastAPI) Setup

```sh
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
alembic upgrade head  # Run DB migrations
uvicorn app.main:app --reload  # Start the backend
```

- The backend will run on `http://localhost:8000` by default.

---

## 4. Frontend (Next.js) Setup

```sh
cd ../../apps/web
cp .env.example .env.local  # Edit API URL as needed
npm install
npm run build
npm run dev
```

- The frontend will run on `http://localhost:3000` by default.
- Ensure `NEXT_PUBLIC_API_URL` in `.env.local` points to your backend (e.g., `http://localhost:8000/api/v1`).

---

## 5. Running the Full Stack

- Start the backend (see above)
- Start the frontend (see above)
- Visit `http://localhost:3000` in your browser

---

## 6. Common Tasks

- **Run backend tests:**
  ```sh
  cd apps/api
  source venv/bin/activate
  pytest
  ```
- **Run frontend tests:**
  ```sh
  cd apps/web
  npm test
  ```
- **Apply DB migrations:**
  ```sh
  cd apps/api
  alembic upgrade head
  ```

---

## 7. Environment Variables

- Backend: `apps/api/.env`
- Frontend: `apps/web/.env.local`

---

## 8. Troubleshooting

- Ensure all `.env` files are present and correct.
- Make sure the backend is running before starting the frontend.
- If you change the backend port, update `NEXT_PUBLIC_API_URL` in the frontend.

---

## 9. Additional Notes

- All authentication and user-related requests from the frontend are proxied to the backend.
- No direct database access or business logic in the frontend.
- For production, configure secure environment variables and use a production-ready server (e.g., Gunicorn for FastAPI, Vercel/Node for Next.js). 