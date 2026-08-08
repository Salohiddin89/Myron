from decimal import Decimal
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from shop.cart import Cart
from shop.models import Product

from .models import Order


def make_product(**overrides):
    defaults = {
        "name_uz": "Order perfume",
        "brand": "MYRON",
        "gender": Product.GENDER_UNISEX,
        "concentration": Product.CONCENTRATION_EDP,
        "volume_ml": 50,
        "price": Decimal("110.00"),
        "stock": 10,
        "image": SimpleUploadedFile("order-perfume.gif", b"GIF89a", content_type="image/gif"),
    }
    defaults.update(overrides)
    return Product.objects.create(**defaults)


class OrderCheckoutTests(TestCase):
    @override_settings(TELEGRAM_SEND_ASYNC=False)
    @patch("orders.views.send_order_to_telegram", return_value=True)
    def test_create_order_from_cart_clears_cart_and_returns_success(self, notify_mock):
        product = make_product()
        session = self.client.session
        request = type("Request", (), {"session": session})()
        cart = Cart(request)
        cart.add(product, 2)
        session.save()

        response = self.client.post(
            reverse("orders:create_order"),
            data={
                "full_name": "Test User",
                "phone": "+998901234567",
                "telegram_username": "@test",
                "message": "Please call first",
            },
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        order = Order.objects.get()
        self.assertEqual(order.full_name, "Test User")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, Decimal("220.00"))
        self.assertEqual(self.client.session["cart"], {})
        notify_mock.assert_called_once()

    def test_create_order_requires_customer_fields_and_cart_items(self):
        response = self.client.post(
            reverse("orders:create_order"),
            data={"full_name": "", "phone": ""},
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("full_name", response.json()["errors"])
        self.assertIn("phone", response.json()["errors"])
        self.assertIn("cart", response.json()["errors"])
