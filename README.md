# 📚 Book Store API

A Django REST Framework project with **JWT authentication**, **admin/user roles**, and **mock payment integration** for purchasing books.

---

## 🚀 Features

- 🔐 JWT-based Authentication (via `djangorestframework-simplejwt`)
- 👨‍💼 Admin Panel:
  - View user statistics
  - Block/unblock users
- 📖 Users can:
  - Browse books
  - Make purchases with mock payment (even card number = success)
- 📄 OpenAPI Documentation (`/swagger/`)
- 🧪 Unit tests included
- 🔒 Role-based permissions

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/s-urunov-dev/task
cd task
```

### 2. Create a Virtual Environment

```bash
python -m venv env
source env/bin/activate  # Windows: env\\Scripts\\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```
### 6. Add test data
```bash
make load
```

### 7. Run the Server

```bash
python manage.py runserver
```

---
