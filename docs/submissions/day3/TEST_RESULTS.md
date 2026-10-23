# Day 3 test cases and results

Executed against Django 5.2.18 with the project's SQLite configuration.

## Automated workflow tests

Run with:

```powershell
$env:DB_ENGINE = "sqlite3"
python manage.py test --verbosity 2
```

| Test case | Expected result | Result |
| --- | --- | --- |
| Register, log in, browse, and search | Account is created and authenticated; the catalog search returns the matching book. | Passed |
| Add to cart and place an order | Checkout creates an order and order item, reduces stock by the ordered quantity, and shows the order in the buyer's history. | Passed |
| Order privacy | A different customer receives a not-found response when opening another user's order. | Passed |
| Staff dashboard summaries | Staff can view book/order counts, confirmed sales, and books at or below the low-stock threshold. | Passed |
| Staff catalog management | Staff can create categories and books. | Passed |
| Non-staff permissions | A regular customer cannot open the dashboard, change order status, or use book/category write pages. | Passed |
| Cancel and reopen order | Cancellation restores stock once; reopening reserves it again and updates sales totals. | Passed |
| Reopen without stock | A cancelled order stays cancelled and stock is unchanged when inventory is insufficient. | Passed |
| Invalid checkout phone | Checkout re-renders the form error and does not create an order. | Passed |

Six Django test methods cover the cases above. Final automated run: **6 tests passed**.

## Project checks

- `python manage.py check`: passed, no issues reported.
- `python manage.py makemigrations --check --dry-run`: passed, no model changes missing migrations.
- The test database applied all project migrations, including the Day 3 order-status migration.

## Manual demonstration flow

1. Register a customer, log in, and search for a book.
2. Add an in-stock quantity to the cart and submit valid delivery details.
3. Confirm the order appears in order history and the book stock has decreased.
4. Log in as staff, open `/dashboard/`, and update the order to Shipped or Cancelled.
5. Confirm cancellation restores inventory and use the Books, Categories, and Orders links to open their Django admin management screens.
