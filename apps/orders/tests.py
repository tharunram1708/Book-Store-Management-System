from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.books.models import Book
from apps.categories.models import Category
from .models import Order, OrderItem


class StoreWorkflowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="A Test Novel", author="A. Writer", isbn="123456789X",
            price=Decimal("12.50"), category=self.category, stock=5,
        )

    def test_register_browse_search_cart_checkout_and_order_history(self):
        register_response = self.client.post(reverse("register"), {
            "username": "reader", "first_name": "Rae", "last_name": "Reader",
            "email": "reader@example.com", "password1": "Strong-demo-pass-481!",
            "password2": "Strong-demo-pass-481!",
        })
        self.assertRedirects(register_response, reverse("book_list"))
        self.assertTrue(self.client.session.get("_auth_user_id"))
        self.client.post(reverse("logout"))
        login_response = self.client.post(reverse("login"), {
            "username": "reader", "password": "Strong-demo-pass-481!",
        })
        self.assertRedirects(login_response, reverse("book_list"))

        self.assertContains(self.client.get(reverse("book_list")), "A Test Novel")
        search_response = self.client.get(reverse("book_list"), {"q": "Test Novel"})
        self.assertContains(search_response, "A Test Novel")
        self.assertEqual(len(search_response.context["books"]), 1)

        self.client.post(reverse("cart_add", args=[self.book.pk]), {"quantity": 2})
        self.assertContains(self.client.get(reverse("cart_detail")), "A Test Novel")
        checkout_response = self.client.post(reverse("checkout"), {
            "shipping_name": "Rae Reader", "shipping_phone": "+91 98765 43210",
            "shipping_address": "12 Main Street, Bengaluru",
        })
        self.assertEqual(checkout_response.status_code, 302)

        order = Order.objects.get(user__username="reader")
        self.assertRedirects(checkout_response, reverse("order_detail", args=[order.pk]))
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 3)
        self.assertEqual(order.items.get().quantity, 2)
        self.assertContains(self.client.get(reverse("order_history")), order.order_number)
        self.assertContains(self.client.get(reverse("order_detail", args=[order.pk])), "A Test Novel")
        stranger = get_user_model().objects.create_user(username="stranger", password="demo-pass")
        self.client.force_login(stranger)
        self.assertEqual(self.client.get(reverse("order_detail", args=[order.pk])).status_code, 404)

    def test_staff_dashboard_updates_status_and_restocks_once_on_cancel(self):
        customer = get_user_model().objects.create_user(username="buyer", password="demo-pass")
        order = self.create_order(customer, status=Order.Status.PENDING)
        self.book.stock = 3
        self.book.save(update_fields=("stock",))
        staff = get_user_model().objects.create_user(username="manager", password="demo-pass", is_staff=True)
        self.client.force_login(staff)

        dashboard = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.context["book_count"], 1)
        self.assertEqual(dashboard.context["order_count"], 1)
        self.assertEqual(dashboard.context["sales_total"], Decimal("0.00"))
        self.assertEqual(dashboard.context["low_stock_count"], 1)

        status_url = reverse("admin_order_status", args=[order.pk])
        self.client.post(status_url, {"status": Order.Status.CANCELLED})
        self.book.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.book.stock, 5)

        self.client.post(status_url, {"status": Order.Status.CANCELLED})
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 5)

        self.client.post(status_url, {"status": Order.Status.CONFIRMED})
        self.book.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)
        self.assertEqual(self.book.stock, 3)
        dashboard = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(dashboard.context["sales_total"], Decimal("25.00"))

    def test_cancelled_order_cannot_reopen_without_stock(self):
        customer = get_user_model().objects.create_user(username="buyer", password="demo-pass")
        order = self.create_order(customer, status=Order.Status.CANCELLED)
        self.book.stock = 0
        self.book.save(update_fields=("stock",))
        staff = get_user_model().objects.create_user(username="manager", password="demo-pass", is_staff=True)
        self.client.force_login(staff)

        response = self.client.post(reverse("admin_order_status", args=[order.pk]), {"status": Order.Status.CONFIRMED})

        self.assertRedirects(response, reverse("admin_dashboard"))
        order.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.book.stock, 0)

    def test_non_staff_cannot_open_admin_or_manage_catalog(self):
        user = get_user_model().objects.create_user(username="reader", password="demo-pass")
        self.client.force_login(user)
        for url_name in ("admin_dashboard", "book_create", "category_create"):
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("admin_order_status", args=[1]), {"status": Order.Status.CANCELLED})
        self.assertEqual(response.status_code, 302)

    def test_staff_can_create_books_and_categories(self):
        staff = get_user_model().objects.create_user(username="manager", password="demo-pass", is_staff=True)
        self.client.force_login(staff)

        category_response = self.client.post(reverse("category_create"), {
            "name": "History", "description": "Historical writing",
        })
        self.assertRedirects(category_response, reverse("category_list"))
        category = Category.objects.get(name="History")

        book_response = self.client.post(reverse("book_create"), {
            "title": "A New History", "author": "H. Writer", "isbn": "9781234567897",
            "price": "19.95", "description": "A test book", "category": category.pk,
            "stock": "4",
        })
        book = Book.objects.get(title="A New History")
        self.assertRedirects(book_response, reverse("book_detail", args=[book.pk]))
        self.assertEqual(book.stock, 4)

    def test_invalid_checkout_phone_shows_form_error_without_creating_order(self):
        user = get_user_model().objects.create_user(username="reader", password="demo-pass")
        self.client.force_login(user)
        self.client.post(reverse("cart_add", args=[self.book.pk]), {"quantity": 1})
        response = self.client.post(reverse("checkout"), {
            "shipping_name": "Reader", "shipping_phone": "123", "shipping_address": "12 Main Street",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertIn("shipping_phone", response.context["form"].errors)

    def create_order(self, user, status):
        order = Order.objects.create(
            user=user, status=status, shipping_name="Test Buyer", shipping_phone="9876543210",
            shipping_address="12 Main Street", subtotal=Decimal("25.00"), total=Decimal("25.00"),
        )
        OrderItem.objects.create(
            order=order, book=self.book, book_title=self.book.title, book_isbn=self.book.isbn,
            unit_price=Decimal("12.50"), quantity=2,
        )
        return order
