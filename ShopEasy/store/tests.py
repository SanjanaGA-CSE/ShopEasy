import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product


class ShopEasyTests(TestCase):
    def setUp(self):
        self.tshirt = Product.objects.create(
            name="T-shirt", description="Cotton", price=Decimal("499.00"), stock=10
        )
        self.watch = Product.objects.create(
            name="Watch", description="Analog", price=Decimal("799.00"), stock=2
        )
        self.user = User.objects.create_user("sanjana", "s@example.com", "pass12345!")

    def post_checkout(self, items):
        return self.client.post(
            reverse("checkout"),
            data=json.dumps({"items": items}),
            content_type="application/json",
        )

    def test_homepage_shows_products(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "T-shirt")
        self.assertContains(response, "Watch")

    def test_search_filters_products(self):
        response = self.client.get(reverse("home"), {"q": "watch"})
        self.assertContains(response, "Watch")
        self.assertNotContains(response, "T-shirt")

    def test_product_detail_page(self):
        response = self.client.get(reverse("product_detail", args=[self.tshirt.pk]))
        self.assertContains(response, "Cotton")

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "n@example.com",
                "password1": "Str0ng!pass99",
                "password2": "Str0ng!pass99",
            },
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_works(self):
        self.assertTrue(self.client.login(username="sanjana", password="pass12345!"))

    def test_checkout_requires_login(self):
        response = self.post_checkout([{"id": self.tshirt.pk, "quantity": 1}])
        self.assertEqual(response.status_code, 401)

    def test_checkout_creates_order_with_server_price(self):
        self.client.login(username="sanjana", password="pass12345!")
        response = self.post_checkout(
            [{"id": self.tshirt.pk, "quantity": 2, "price": "1"}]  # fake price ignored
        )
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get()
        self.assertEqual(order.total, Decimal("998.00"))
        self.assertEqual(order.items.count(), 1)
        self.tshirt.refresh_from_db()
        self.assertEqual(self.tshirt.stock, 8)

    def test_checkout_rejects_empty_cart(self):
        self.client.login(username="sanjana", password="pass12345!")
        self.assertEqual(self.post_checkout([]).status_code, 400)

    def test_checkout_rejects_bad_quantity(self):
        self.client.login(username="sanjana", password="pass12345!")
        self.assertEqual(
            self.post_checkout([{"id": self.tshirt.pk, "quantity": 0}]).status_code, 400
        )

    def test_checkout_rejects_more_than_stock(self):
        self.client.login(username="sanjana", password="pass12345!")
        response = self.post_checkout([{"id": self.watch.pk, "quantity": 5}])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_my_orders_requires_login(self):
        response = self.client.get(reverse("my_orders"))
        self.assertEqual(response.status_code, 302)
