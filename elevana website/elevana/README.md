This document provides a comprehensive overview of the Elevana project, covering the architecture, configuration, and setup steps we have designed.

You can copy the content below directly into a file named **`README.md`** in your project root.

---

```markdown
# Elevana Professional Training Institute Platform

Elevana is a professional training and learning management platform designed to empower professionals across Africa. This platform is built using **Django**, a high-level Python web framework, following a modular and scalable architecture.

## 🚀 Technology Stack
* **Backend:** Django 4.x / 5.x
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Frontend:** HTML5, Bootstrap 4, CSS3
* **Deployment:** AWS (ECS/App Runner)
* **Static Assets:** Managed via Django `static` configuration

## 📂 Project Structure
The project follows a clean, decoupled architecture:
```text
elevana_project/
├── apps/               # Business logic modules
│   ├── main/           # Home, About, Contact pages
│   └── courses/        # Course catalog and management
├── core/               # Project-wide settings and routing
├── static/             # Global CSS, JS, and Images
├── templates/          # Global layout (base.html, includes/)
└── manage.py           # Django CLI

```

## 🛠 Setup & Installation

### 1. Prerequisites

* Python 3.10+
* `pip` package manager

### 2. Initialization

```bash
# Clone the repository
git clone <your-repository-url>
cd elevana_project

# Setup Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Database & Migrations

```bash
# Create initial database schema
python manage.py makemigrations
python manage.py migrate

# Create Admin account
python manage.py createsuperuser

```

### 4. Running the Development Server

```bash
python manage.py runserver

```

## ⚙️ Key Configuration Details

### Settings (`settings.py`)

To maintain the custom `apps/` directory, the following configurations were applied:

* **`sys.path.append`**: Added `apps/` to the Python path.
* **`INSTALLED_APPS`**: Registered as `'apps.main'` and `'apps.courses'`.
* **`TEMPLATES`**: Configured to look in both the root `templates/` folder and individual app `templates/` folders.

### URL Routing

The project uses a two-tier routing system:

1. **Root (`core/urls.py`)**: Includes `apps.main.urls` and `apps.courses.urls`.
2. **App-level**: Handles specific views (e.g., `course_list`, `course_detail`). Use the `{% url 'name' %}` tag for dynamic link generation.

## 🔑 Security & Permissions

* **Access Control**: Staff-only access for course management (`manage_course`) is enforced using the `@user_passes_test(staff_only)` decorator.
* **Authentication**: `login_required` is implemented for all administrative actions.

## 💡 Deployment Notes (AWS)

1. **Static Files**: Run `python manage.py collectstatic` to aggregate assets.
2. **Environment Variables**: Always store `SECRET_KEY`, `DEBUG`, and Database Credentials in an `.env` file.
3. **Allowed Hosts**: Ensure your domain/IP is added to `ALLOWED_HOSTS` in `settings.py`.

## 🤝 Contributing

1. Create a branch for your feature: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`

## 📧 Contact

For technical inquiries or project documentation support, please contact the development team.

```

```