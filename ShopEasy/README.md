# ShopEasy: Simple E-commerce Store

CodeAlpha Full Stack Development Internship, Task 1.

A beginner-level e-commerce website built with HTML, CSS and JavaScript on the frontend and Django (Python) on the backend, using SQLite as the database.

## Features
- Product listings with images, names, prices and a search bar
- Product details page (image, name, price, description, Add to Cart)
- Shopping cart (browser localStorage): add, remove, increase/decrease quantity, item count, total price
- User registration, login and logout (Django authentication, hashed passwords)
- Order processing: the server validates products and quantities, reads prices from the database, calculates the total, checks stock, and creates the Order and OrderItems (simulated checkout, no real payment)
- Order confirmation page and "My orders" history
- Admin panel to add and manage products, view orders
- Automated tests

## Tech stack
HTML, CSS (Flexbox/Grid, responsive), JavaScript, Python, Django, SQLite

## Project structure
```
ShopEasy/
├── manage.py
├── requirements.txt
├── config/            # Django settings and root urls
├── store/             # models, views, urls, forms, admin, tests
├── templates/         # base, index (home), product, cart, login, register, orders
└── static/            # css/style.css, js/script.js, images/
```

## How to run
1. Install Python 3.10 or newer.
2. Open a terminal in the project folder, then:
```
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python manage.py makemigrations store
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```
3. Open http://127.0.0.1:8000/ for the store and http://127.0.0.1:8000/admin/ for the admin panel.

## Run the tests
```
python manage.py test
```

## Screenshots
Add screenshots of the homepage, product page, cart, login/register and order confirmation here.

## Author
Sanjana G A
