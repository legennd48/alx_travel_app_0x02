# alx_travel_app

This is a Django-based backend project for managing travel listings, bookings, and reviews.

## Features

- **Listings:** Create and manage travel property listings.
- **Bookings:** Book available listings for specific dates.
- **Reviews:** Leave reviews and ratings for listings.
- **REST API:** Built with Django REST Framework.
- **Swagger Documentation:** API docs available at `/swagger/`.
- **MySQL Database:** Configured via environment variables.
- **CORS Support:** Enabled for frontend integration.
- **Database Seeder:** Populate the database with sample data using a custom management command.

## Project Structure

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

## Setup

1. Install dependencies:  
   `pip install -r requirements.txt`
2. Configure your `.env` file for database and secret key.
3. Run migrations:  
   `python manage.py migrate`
4. Seed the database:  
   `python manage.py seed`
5. Start the server:  
   `python manage.py runserver`

---

**Note:**  
This project is under active development and will be expanded with more features.