# CodeAlpha Store — Django E-commerce Starter

A basic e-commerce website built with Django, SQLite, HTML, CSS and JavaScript.

## Features
- Product listing and product detail pages
- Session-based shopping cart (add, update quantity, remove)
- User registration, login and logout
- Checkout and order creation
- Order history for signed-in users
- Django admin for managing products and reviewing orders
- SQLite database (created automatically through migrations)

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/  
Admin: http://127.0.0.1:8000/admin/

## Notes before production
This is a learning starter, not a production-ready store. Set a strong `DJANGO_SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`, use HTTPS, and use a production database/server before deployment. Payment processing is intentionally not included; checkout records a cash-on-delivery/demo order. Never store card details yourself.
