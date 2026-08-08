from decimal import Decimal
from types import SimpleNamespace

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .cart import Cart
from .context_processors import cart_context
from .models import Product


def make_product(**overrides):
    defaults = {
        "name_uz": "Test perfume",
        "brand": "MYRON",
        "gender": Product.GENDER_UNISEX,
        "concentration": Product.CONCENTRATION_EDP,
        "volume_ml": 50,
        "price": Decimal("88.00"),
        "stock": 10,
        "image": SimpleUploadedFile("perfume.gif", b"GIF89a", content_type="image/gif"),
    }
    defaults.update(overrides)
    return Product.objects.create(**defaults)


class CartTests(TestCase):
    def test_cart_context_counts_current_and_legacy_session_formats(self):
        request = SimpleNamespace(session={"cart": {"1": {"quantity": 2}, "2": 3}})

        self.assertEqual(cart_context(request), {"cart_count": 5})

    def test_cart_add_returns_updated_drawer_json(self):
        product = make_product()

        response = self.client.post(
            reverse("shop:cart_add"),
            data={"product_id": product.pk, "quantity": 1},
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertIn("cart-items", response.json()["html"])

    def test_cart_normalizes_legacy_session_values(self):
        session = self.client.session
        session["cart"] = {"1": 2, "2": {"quantity": 3}, "bad": "x"}
        session.save()

        request = SimpleNamespace(session=session)
        cart = Cart(request)

        self.assertEqual(len(cart), 5)
        self.assertEqual(cart.cart, {"1:full": {"quantity": 2}, "2:full": {"quantity": 3}})

    def test_cart_keeps_ml_variants_as_separate_items(self):
        product = make_product(
            sell_by_ml=True,
            price_10ml=Decimal("18.00"),
            price_20ml=Decimal("32.00"),
        )
        request = SimpleNamespace(session=self.client.session)
        cart = Cart(request)

        cart.add(product, quantity=1, variant_code="full")
        cart.add(product, quantity=2, variant_code="10")

        items = sorted(cart.get_items(), key=lambda item: item["variant_code"])
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["variant_code"], "10")
        self.assertEqual(items[0]["variant_price"], Decimal("18.00"))
        self.assertEqual(items[0]["subtotal"], Decimal("36.00"))
        self.assertEqual(items[1]["variant_code"], "full")
        self.assertEqual(items[1]["variant_price"], Decimal("88.00"))
