from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    """Simple session-backed shopping cart. No page reload required —
    all interactions happen through small AJAX endpoints in views.py."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        normalized = {}
        changed = False
        for raw_key, item in cart.items():
            try:
                quantity = int(item.get("quantity", 0) if isinstance(item, dict) else item)
            except (TypeError, ValueError):
                changed = True
                continue
            if quantity <= 0:
                changed = True
                continue
            product_id, variant_code = self.parse_key(raw_key)
            key = self.make_key(product_id, variant_code)
            normalized[key] = {"quantity": normalized.get(key, {}).get("quantity", 0) + quantity}
            if key != raw_key or normalized[key] != item:
                changed = True
        if changed:
            cart = self.session[settings.CART_SESSION_ID] = normalized
            self.session.modified = True
        self.cart = cart

    @staticmethod
    def make_key(product_id, variant_code="full"):
        return f"{product_id}:{variant_code or 'full'}"

    @staticmethod
    def parse_key(key):
        product_id, sep, variant_code = str(key).partition(":")
        return product_id, variant_code if sep else "full"

    def add(self, product, quantity=1, variant_code="full"):
        variant = product.get_variant(variant_code)
        item_key = self.make_key(product.id, variant["code"])
        if item_key not in self.cart:
            self.cart[item_key] = {"quantity": 0}
        self.cart[item_key]["quantity"] += quantity
        self.save()

    def set_quantity(self, product, quantity, variant_code="full"):
        item_key = self.make_key(product.id, product.get_variant(variant_code)["code"])
        if quantity <= 0:
            self.remove(product, variant_code)
            return
        self.cart[item_key] = {"quantity": quantity}
        self.save()

    def remove(self, product, variant_code="full"):
        item_key = self.make_key(product.id, product.get_variant(variant_code)["code"])
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def __iter__(self):
        product_ids = [self.parse_key(key)[0] for key in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for item_key, item in self.cart.items():
            product_id, variant_code = self.parse_key(item_key)
            product = products_map.get(product_id)
            if not product:
                continue
            variant = product.get_variant(variant_code)
            yield {
                "key": item_key,
                "product": product,
                "variant_code": variant["code"],
                "variant_label": variant["label"],
                "variant_price": variant["price"],
                "variant_volume_ml": variant["volume_ml"],
                "quantity": item["quantity"],
                "subtotal": variant["price"] * item["quantity"],
            }

    def __len__(self):
        return sum(int(item.get("quantity", 0)) for item in self.cart.values())

    def get_total_price(self):
        total = Decimal("0")
        for item in self:
            total += item["subtotal"]
        return total

    def get_items(self):
        return list(self)
