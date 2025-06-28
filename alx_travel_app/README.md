# alx_travel_app

A Django-based travel listing platform, serving as the foundation for a scalable, production-ready backend. This project is part of a multi-stage learning experience and will be expanded with more features in future milestones.

## Milestone 1: Setup, Database Configuration, and Seeding

### Overview

This milestone focuses on setting up the initial project structure, configuring a robust MySQL database, integrating essential tools for API documentation, and establishing maintainable configurations. It also includes creating database models, serializers, and a management command for seeding the database with sample data.

### Key Objectives

- **Project Initialization:**  
  - Create a Django project named `alx_travel_app`.
  - Add an app named `listings` for core functionalities.

- **Dependency Management:**  
  - Install and configure the following packages:
    - `django`
    - `djangorestframework`
    - `django-cors-headers`
    - `drf-yasg` (Swagger API documentation)
    - `celery` and `rabbitmq` (for future background tasks)

- **Settings Configuration:**  
  - Use `django-environ` to manage environment variables securely via a `.env` file.
  - Configure MySQL as the primary database, with credentials loaded from environment variables.
  - Set up Django REST Framework and CORS headers.

- **Swagger Integration:**  
  - Integrate Swagger using `drf-yasg` to automatically document all APIs.
  - Make API documentation accessible at `/swagger/`.

- **Version Control:**  
  - Initialize a Git repository.
  - Commit all setup files and push to a GitHub repository named `alx_travel_app_0x00`.

- **Database Models and Serializers:**  
  - Define `Listing`, `Booking`, and `Review` models in `listings/models.py`.
  - Create serializers for these models in `listings/serializers.py`.

- **Database Seeder:**  
  - Implement a management command in `listings/management/commands/seed.py` to populate the database with sample data.

### Project Structure

```
alx_travel_app/
├── listings/
│   ├── models.py
│   ├── serializers.py
│   ├── management/
│   │   └── commands/
│   │       └── seed.py
│   └── README.md
├── alx_travel_app/
│   ├── settings.py
│   ├── urls.py
├── requirements.txt
├── .env
└── README.md
```

### Tasks Checklist

- [x] Initialize Django project and `listings` app
- [x] Install all required dependencies
- [x] Configure MySQL database using environment variables
- [x] Set up Django REST Framework and CORS headers
- [x] Integrate Swagger documentation at `/swagger/`
- [x] Initialize Git repository and make initial commit
- [x] Define models and serializers for `Listing`, `Booking`, and `Review`
- [x] Implement and test database seeder command

---

## Setup Instructions

1. **Install dependencies:**  
   `pip install -r requirements.txt`

2. **Configure environment:**  
   Create a `.env` file with your database and secret key settings.

3. **Apply migrations:**  
   `python manage.py migrate`

4. **Seed the database:**  
   `python manage.py seed`

5. **Run the development server:**  
   `python manage.py runserver`

6. **Access Swagger API docs:**  
   Visit `http://localhost:8000/swagger/`

---

**Note:**  
This is the first milestone. The project will be expanded in future stages to add more features and functionalities.
