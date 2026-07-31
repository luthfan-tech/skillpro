# 🎓 SkillPro — Modern Learning Management System (LMS)

SkillPro is a lightweight, modular Learning Management System built with **Python (Flask)**, **SQLAlchemy**, and **Bootstrap 5**. It includes role-based access control, dynamic course authoring, automated quiz grading, leaderboards, and printable completion certificates.

> Built with AI assistance, then reviewed, customized, and structured by me to ensure clean architecture, maintainability, and a polished user experience.

---

## 🚀 Features

- **Role-Based Portals** — Separate, tailored experiences for **students** and **instructors**.
- **Course Catalog** — Full-text search, category filtering, and progress tracking.
- **Curriculum Builder** — Structured learning paths with courses, modules, and lessons.
- **Quiz Engine** — Automated evaluation with real-time feedback and best-attempt mapping.
- **Verifiable Certificates** — Auto-generated certificates with unique verification codes after 100% completion.
- **Leaderboard** — Student ranking based on total completed lessons.
- **AI Doubt Solver** — Embedded assistant inside the lesson player for contextual help.

---

## 🛠️ Project Structure

```text
skillpro/
├── app.py            # Application factory and route entry points
├── config.py         # Environment and database configuration
├── extensions.py     # Flask extension setup (DB, LoginManager)
├── models/           # SQLAlchemy models (User, Course, Progress, etc.)
├── routes/           # Modular Blueprint routes
├── services/         # Business logic (CourseService, CertificateService)
├── static/           # Custom CSS, JS, and React components
├── templates/        # Jinja2 templates and error pages
├── .env.example      # Example environment variables
├── .gitignore        # Git ignore rules
└── seed.py           # Database seeding script
```

---

## ⚡ Quick Start

### 1. Prerequisites

- Python **3.10+**
- Git

### 2. Installation

```bash
git clone https://github.com/luthfan-tech/skillpro.git
cd skillpro

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install flask flask-sqlalchemy flask-login werkzeug
```

### 3. Environment Configuration

```bash
cp .env.example .env
```

Update `.env` with your local settings:

```env
SECRET_KEY=your-super-secret-key
FLASK_APP=app.py
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=sqlite:///skillpro.db
```

### 4. Database Setup & Seeding

Start the app and run the setup route:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/setup-db
```

This initializes the SQLite database and seeds demo data.

---

## 🔐 Demo Credentials

| Role        | Email                 | Password     |
|------------|-----------------------|--------------|
| Admin      | admin@skillpro.com    | admin123     |
| Instructor | admin@skillpro.com    | admin123     |
| Student    | student@skillpro.com  | student123   |
