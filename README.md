# GymBro Backend 🏋️‍♂️💪

Welcome to the **GymBro Backend**! This repository houses the robust REST API that powers the GymBro application—an interactive workout tracker, anatomical muscle-mapping index, and social fitness platform.

Built with Python, Django, and Django REST Framework, the backend provides highly scalable, secure, and well-documented endpoints for user profiles, workout plans, muscle/exercise databases, blog articles, and social networking with other "gym bros".

---

## 🚀 Key Features

*   **🔒 Secure Authentication:** JWT-based user authentication using `djangorestframework-simplejwt`.
*   **👤 User & Profile Management:** Custom user profiles with specific gym targets, progress metrics, and preferences.
*   **🧠 Gym Bro IQ (Exercises & Muscles):** A detailed anatomical index of muscle groups and exercises to help users understand their training anatomy.
*   **📋 Workout Engine:** Full CRUD for creating custom workout plans, tracking reps/sets/weights, and logging active training sessions.
*   **🤝 Gym Bros Social Network:** Connect with friends ("bros"), view their profiles, and share or assign workout routines directly to them.
*   **🔔 Notification Center:** Instant updates when users receive incoming bro requests, workout assignments, or activity updates.
*   **📖 Blog Service:** Read and manage fitness, diet, and scientific articles with localization support.
*   **🔌 Swagger OpenAPI Documentation:** Auto-generated interactive API docs using `drf-spectacular` at `/api/docs/`.

---

## 🛠️ Technology Stack

*   **Framework:** [Django](https://www.djangoproject.com/) 5.2.10
*   **API Toolkit:** [Django REST Framework (DRF)](https://www.django-rest-framework.org/) 3.16.0
*   **Database:** [PostgreSQL](https://www.postgresql.org/) 15 (connected via `psycopg` 3.3.2)
*   **Authentication:** [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) 5.5.0
*   **Documentation:** [drf-spectacular](https://drf-spectacular.readthedocs.io/) 0.29.0 (OpenAPI 3.0 + Swagger UI)
*   **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## 📁 Repository Structure

```directory
GymBro-Backend/
├── apps/                 # Django App modules
│   ├── blog/             # Articles, comments, and resources
│   ├── bros/             # Friends and social features (follow, invite)
│   ├── exercises/        # Muscles anatomical map and exercise index (Gym Bro IQ)
│   ├── notifications/    # Internal notifications service
│   ├── users/            # Custom User model, auth logic, and profiles
│   └── workouts/         # Workout builder, session logs, and tracking
├── config/               # Project configuration, settings, and main URLs
├── docker/               # Dockerfiles and container configurations
├── scripts/              # Shell scripts for container entrypoints/automation
├── docker-compose.yml    # Development Docker orchestration
├── manage.py             # Django management CLI
└── requirements.txt      # Python dependencies
```

---

## ⚡ Quick Start Guide

### Option 1: Docker Compose (Recommended)

Running the entire ecosystem (Django API + PostgreSQL Database) in Docker is the fastest way to get started.

1.  **Duplicate the environment variables file:**
    ```bash
    cp .env.example .env
    ```
    *(The default variables are preconfigured to work immediately with Docker!)*

2.  **Spin up the services:**
    ```bash
    docker-compose up --build
    ```
    This command will:
    *   Initialize and health-check the PostgreSQL container.
    *   Build the Django backend container.
    *   Run database migrations automatically.
    *   Collect static files.
    *   Start the development server at `http://localhost:8000`.

### Option 2: Local Manual Setup

If you prefer to run the backend natively:

1.  **Clone/Navigate to the directory & set up a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

2.  **Install the dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory and specify your local PostgreSQL database credentials:
    ```env
    COMPOSE_PROJECT_NAME=gymbro
    DB_NAME=gymbro
    DB_USER=your_postgres_user
    DB_PASSWORD=your_postgres_password
    DB_HOST=localhost
    DB_PORT=5432
    ```

4.  **Run migrations and start the server:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
    The server will be live at `http://127.0.0.1:8000`.

---

## 🔌 API Endpoints Reference

The backend exposes the following primary routing sections:

| Context | Base Path | Description |
| :--- | :--- | :--- |
| **Authentication & Users** | `/api/users/` | User signup, JWT token claims (login, refresh), and profile access. |
| **Gym & Workouts** | `/api/gym/` | Manage workout programs, custom schedules, and ongoing exercise logs. |
| **Gym Bro IQ** | `/api/iq/` | anatomical muscles data and exercises encyclopedia. |
| **Social / Bros** | `/api/bros/` | Friend search, pending requests, accept/decline, and shared assignments. |
| **Blog** | `/api/blog/` | High-quality fitness writeups and scientific resources. |
| **API Schema** | `/api/schema/` | Raw OpenAPI 3.0 schema generation. |
| **Swagger UI** | `/api/docs/` | Interactive browser page to view and test all APIs. |

---

## 🧪 Testing

To run the automated suite:
```bash
# Inside Docker:
docker-compose exec web python manage.py test

# Local:
python manage.py test
```

---

## 🤝 Contribution Guidelines

1.  Keep views thin and business logic inside the `services.py` layers.
2.  Document newly created models or serializers to keep the Swagger documentation precise.
3.  Ensure database migrations are fully committed and tested.

Let's get those gains! 🚀🏋️‍♂️
