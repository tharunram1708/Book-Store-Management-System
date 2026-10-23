# PageTurner Bookstore

A Django bookstore and inventory application built in two project days. MySQL is the default database; SQLite is available for local development and demonstrations.

## Project layout

```text
apps/                 Django domain apps
  accounts/           Registration, authentication, and profiles
  books/              Catalog and book management
  categories/         Category management
  cart/               Persistent user carts
  orders/               Checkout, order history, and status
  dashboard/          Home route
config/               Django settings, root URLs, ASGI, and WSGI
templates/            Shared and app-specific HTML templates
static/               CSS and other static assets
media/                Uploaded book covers (local only)
docs/submissions/     Day 1 and Day 2 screenshot evidence
deliverables/         Submission archives
manage.py             Django management entry point
```

## Setup

1. Create and activate a virtual environment, then install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Create a MySQL database named `bookstore_db` (or change `DB_NAME`). Copy `.env.example` to `.env` and add your database credentials and a private `SECRET_KEY`.

   To use SQLite locally, set `$env:DB_ENGINE='sqlite3'` before running Django commands.

3. Apply migrations and create an admin account:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

   Open `http://127.0.0.1:8000/`. Add categories in `/categories/` or Django admin before adding books. Registration and book management are available in the site navigation.

## Features

- Registration, login/logout, profile editing, and protected account pages.
- Book search by title, author, or ISBN; category and price filters; title, price, and date sorting.
- Book and category create, edit, and delete flows.
- Book catalog fields: title, author, ISBN, price, description, category, stock, and cover image.
- Persistent per-user carts with quantity updates, item removal, subtotal, and total.
- Checkout rechecks stock while locking cart and book rows, creates an order and order items, decrements stock in one database transaction, and clears the cart.
- Order history and detail pages with status tracking. Staff can update order status in Django admin.
- Bootstrap templates and development-time book cover uploads.

## Deliverables

- [Day 1 submission notes and screenshots](docs/submissions/day1/README.md)
- [Day 2 submission notes and screenshots](docs/submissions/day2/README.md)
- Day 1 archive: `deliverables/day1/day1-submission.zip`
- Day 2 archive: `deliverables/day2/day2-submission.zip`
