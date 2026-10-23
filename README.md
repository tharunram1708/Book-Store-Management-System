# PageTurner Bookstore

A Django bookstore and inventory application with customer accounts, searchable book listings, a persistent cart, checkout, order history, and a staff dashboard.

## Features

- Register, log in, update a profile, browse books, and filter by title, author, ISBN, category, and price.
- Add books to a persistent cart and update quantities with stock validation.
- Place orders with a database transaction that checks stock, creates order items, decrements inventory, and empties the cart.
- View private order history and order details.
- Open the staff dashboard at `/dashboard/` for book, order, sales, and low-stock summaries.
- Manage books, categories, and orders through the dashboard links to Django admin.
- Update order statuses to Pending, Confirmed, Shipped, Delivered, or Cancelled. Cancelling restores inventory once; reopening a cancelled order checks and reserves stock again.
- Manage book and category records only as staff. Customer pages and order records remain scoped to their owners.

## Requirements

- Python 3.10 or newer
- pip
- SQLite for the local demo, or MySQL 8+ for a MySQL setup

Install dependencies in a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run locally with SQLite

SQLite is convenient for development and the complete workflow tests. In PowerShell:

```powershell
$env:DB_ENGINE = "sqlite3"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit <http://127.0.0.1:8000/> for the store, <http://127.0.0.1:8000/dashboard/> for the staff dashboard, and <http://127.0.0.1:8000/admin/> for Django admin. Add categories and books using Django admin or the staff links, then register a regular customer account to run through checkout.

To use a separate SQLite file, set `SQLITE_NAME` to its path before running the commands. By default the project uses `db.sqlite3` in the project directory.

## Run with MySQL

Copy `.env.example` to `.env`, create a MySQL database, and set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. Keep a private `SECRET_KEY` in `.env`. Leave `DB_ENGINE` unset (or set it to `mysql`), then run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Never commit `.env`, database files, or uploaded book covers. `.env.example` contains placeholders only.

## Tests

Run the automated workflow and permission tests with SQLite:

```powershell
$env:DB_ENGINE = "sqlite3"
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

The tests cover registration, browsing and searching, cart and checkout, stock decrement, order history, staff dashboard summaries, cancellation and restocking, insufficient stock on reopening, non-staff access restrictions, and invalid checkout input. The manual scenario and results are recorded in [Day 3 test results](docs/submissions/day3/TEST_RESULTS.md).

## Submission material

- [Day 1 notes and screenshots](docs/submissions/day1/README.md)
- [Day 2 notes and screenshots](docs/submissions/day2/README.md)
- [Day 3 notes, test results, and screenshots](docs/submissions/day3/README.md)
- `requirements.txt` lists runtime dependencies.
