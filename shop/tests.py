import json
from decimal import Decimal
from types import SimpleNamespace

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .cart import Cart
from .context_processors import cart_context
from .models import Product, ProductVote


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


class ProductVoteTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.url = reverse("shop:product_vote", args=[self.product.slug])

    def vote(self, vote_type, choice):
        return self.client.post(
            self.url,
            data=json.dumps({"vote_type": vote_type, "choice": choice}),
            content_type="application/json",
        )

    def test_rating_vote_can_be_replaced_and_cleared(self):
        response = self.vote(Product.VOTE_TYPE_RATING, "love")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["selected"], "love")
        self.assertEqual(response.json()["counts"], {"love": 1})

        response = self.vote(Product.VOTE_TYPE_RATING, "hate")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["selected"], "hate")
        self.assertEqual(response.json()["counts"], {"hate": 1})
        self.assertEqual(
            ProductVote.objects.filter(
                product=self.product,
                vote_type=Product.VOTE_TYPE_RATING,
            ).count(),
            1,
        )

        response = self.vote(Product.VOTE_TYPE_RATING, "hate")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["selected"])
        self.assertEqual(response.json()["counts"], {})

    def test_wear_vote_is_independent_from_rating_vote(self):
        self.assertEqual(
            self.vote(Product.VOTE_TYPE_RATING, "like").status_code,
            200,
        )
        response = self.vote(Product.VOTE_TYPE_WEAR, "winter")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["selected"], "winter")
        self.assertEqual(response.json()["counts"], {"winter": 1})
        self.assertEqual(ProductVote.objects.filter(product=self.product).count(), 2)

    def test_disabled_vote_group_rejects_votes(self):
        self.product.show_user_rating = False
        self.product.save(update_fields=["show_user_rating"])

        response = self.vote(Product.VOTE_TYPE_RATING, "love")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["ok"], False)

    def test_product_detail_renders_vote_groups_and_counts(self):
        response = self.client.get(
            reverse("shop:product_detail", args=[self.product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pd-votes-section")
        self.assertContains(response, 'data-vote-type="rating"')
        self.assertContains(response, 'data-vote-type="wear"')
        self.assertContains(response, "data-vote-count")
        self.assertContains(response, "Foydalanuvchi bahosi")
        self.assertNotContains(response, "User Rating")
        self.assertNotContains(response, "When to wear")

    def test_product_detail_vote_labels_follow_selected_language(self):
        url = reverse("shop:product_detail", args=[self.product.slug])

        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE="ru")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Оценка пользователей")
        self.assertContains(response, "Когда носить")
        self.assertContains(response, "Обожаю")
        self.assertNotContains(response, "User Rating")

    def test_product_detail_renders_fragrance_pyramid_in_order(self):
        self.product.top_notes_uz = "Bergamot, Limon"
        self.product.heart_notes_uz = "Atirgul\nYasmin"
        self.product.base_notes_uz = "Vanil, Mushk"
        self.product.save(
            update_fields=["top_notes_uz", "heart_notes_uz", "base_notes_uz"]
        )

        response = self.client.get(
            reverse("shop:product_detail", args=[self.product.slug]),
            HTTP_ACCEPT_LANGUAGE="uz",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pd-note-list")
        self.assertContains(response, "Hid notalari")
        self.assertContains(response, "Bergamot")
        self.assertContains(response, "Yasmin")
        self.assertContains(response, "Mushk")
        self.assertLess(response.content.find(b"Bergamot"), response.content.find(b"Yasmin"))
        self.assertLess(response.content.find(b"Yasmin"), response.content.find(b"Mushk"))

    def test_product_detail_uses_russian_fragrance_notes(self):
        self.product.top_notes_uz = "Bergamot"
        self.product.top_notes_ru = "Бергамот"
        self.product.save(update_fields=["top_notes_uz", "top_notes_ru"])

        response = self.client.get(
            reverse("shop:product_detail", args=[self.product.slug]),
            HTTP_ACCEPT_LANGUAGE="ru",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ноты аромата")
        self.assertContains(response, "Верхняя нота")
        self.assertContains(response, "Бергамот")
        self.assertNotContains(response, "Bergamot")
