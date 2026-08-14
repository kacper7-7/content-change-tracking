# Content Change Tracking API

A modern API based on the Django framework and Django REST Framework, used for managing content, following posts, and tracking change history. The project utilizes an asynchronous architecture using Celery and Redis to handle notifications and periodic background tasks.

## Main Features

*   **User Management**: 
    *   Custom user model logging in using an email address instead of a username.
    *   Handling authorization and creating new accounts (public access to registration, hidden details for other users).
*   **Content Management and Change Tracking**:
    *   Creating, reading, and editing own content.
    *   Tracking edit history (`ContentEditHistory`) and the number of modifications.
    *   Caching system speeding up the retrieval of updated content.
*   **Following and Notifications**:
    *   Ability to follow specific posts.
    *   Checking unread changes (`has_new_changes`) and the number of missed edits.
    *   Asynchronous creation of notifications for followers when content is changed (using Celery).
*   **Background Tasks (Celery)**:
    *   Automatic deletion of inactive content older than a year using the Celery Beat scheduler.

---

## Technologies

*   **Language:** Python 3
*   **Framework:** Django, Django REST Framework
*   **Asynchrony:** Celery
*   **Message Broker / Cache:** Redis, Docker
*   **Documentation:** drf-spectacular (OpenAPI / Swagger UI)
*   **Tests:** `django.test.TestCase` for models and views

---

## Running the project (Locally)

To run all project components, follow the instructions below. 4 separate terminal sessions are required.

### Step 1: Clone the repository

First, clone the repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/kacper7-7/content-change-tracking.git
cd content-change-tracking
```

### Step 2: Virtual Environment and Dependencies

Create a virtual environment, activate it, and install the required packages.

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Environment Variables

Create a `.env` file in the root directory of the project and add your Django secret key.

```env
SECRET_KEY=your-super-secret-key-here
```

### Step 4: Starting the Redis broker

Redis is essential as a message broker for Celery and for caching.

```bash
docker start my_redis
```

### Step 5: Migrations and starting the server (Main terminal)

Apply database migrations, create an admin account, and start the API server.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Step 6: Starting Celery Worker

This process handles asynchronous tasks, including sending notifications after editing a post.

```bash
celery -A content_change_tracking worker --pool=solo -l INFO
```

### Step 7: Starting Celery Beat

The scheduler process responsible for periodic tasks (e.g., nightly removal of old posts).

```bash
celery -A content_change_tracking beat -l INFO
```

---

## Available API Endpoints

All core API endpoints are prefixed with `/api/`.

| Resource | Endpoint | Available Methods | Description                                                                                 |
| :--- | :--- | :--- |:--------------------------------------------------------------------------------------------|
| **Users** | `/api/users/` | `GET`, `POST`, `PATCH` | Registration, retrieving profiles, and editing own account.                                 |
| **Content** | `/api/content/` | `GET`, `POST`, `PATCH`, `DELETE` | Managing posts. Retrieving information about `recent_edits_count` or `followers_count`.     |
| **Updated** | `/api/content/updated-contents/` | `GET` | Displays the latest modified content that the user follows (uses Cache).                    |
| **Follows** | `/api/follows/` | `GET`, `POST`, `DELETE` | Following and unfollowing content.                                              |
| **Notifications** | `/api/notifications/` | `GET` | Receiving notifications assigned to the logged-in user (`ReadOnlyModelViewSet`). |

### Interactive API Documentation

Once the server is running, you can explore and interact with the API using the auto-generated Swagger UI interface available at:
*   **Swagger UI:** `http://127.0.0.1:8000/api/docs/`

---

## Running Tests

The project has comprehensive automated tests written for all applications (users, content, notifications). To run the entire test suite, use the command:

```bash
python manage.py test
```