import json
import threading

from django.conf import settings
from django.db import close_old_connections
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from shop.cart import Cart
from .models import Order, OrderItem
from .utils import send_order_to_telegram


def _notify_order(order_id):
    try:
        close_old_connections()
        order = Order.objects.prefetch_related("items__product").get(pk=order_id)
        send_order_to_telegram(order)
    finally:
        close_old_connections()


def notify_order(order):
    if getattr(settings, "TELEGRAM_SEND_ASYNC", True):
        thread = threading.Thread(target=_notify_order, args=(order.pk,), daemon=True)
        thread.start()
        return
    send_order_to_telegram(order)


@require_POST
def create_order(request):
    try:
        data = json.loads(request.body) if request.body else request.POST
    except json.JSONDecodeError:
        data = request.POST

    full_name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    telegram_username = (data.get("telegram_username") or "").strip()
    message = (data.get("message") or "").strip()

    errors = {}
    if not full_name:
        errors["full_name"] = _("Ism familiyangizni kiriting")
    if not phone:
        errors["phone"] = _("Telefon raqamingizni kiriting")

    cart = Cart(request)
    if len(cart) == 0:
        errors["cart"] = _("Savatingiz bo'sh")

    if errors:
        return JsonResponse({"success": False, "errors": errors}, status=400)

    order = Order.objects.create(
        full_name=full_name,
        phone=phone,
        telegram_username=telegram_username,
        message=message,
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            product_name=item["product"].name_uz,
            product_price=item["variant_price"],
            variant_label=item["variant_label"],
            variant_volume_ml=item["variant_volume_ml"],
            quantity=item["quantity"],
        )

    order.recalc_total()
    cart.clear()
    notify_order(order)

    return JsonResponse({"success": True, "order_id": order.pk})
