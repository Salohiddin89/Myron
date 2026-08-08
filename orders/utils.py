import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_to_telegram(order):
    """Send a formatted message about a new order to the admin's Telegram chat.

    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID to be set
    (via environment variables or directly in settings.py). If they are not
    configured, this silently does nothing except log a warning, so the
    website keeps working while the bot is being set up.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_ADMIN_CHAT_ID

    if not token or not chat_id:
        logger.warning(
            "TELEGRAM_BOT_TOKEN yoki TELEGRAM_ADMIN_CHAT_ID sozlanmagan — "
            "buyurtma #%s haqida xabar yuborilmadi.", order.pk
        )
        return False

    lines = [
        "🛍 <b>YANGI BUYURTMA</b> #%s" % order.pk,
        "",
        "👤 <b>Ism familiya:</b> %s" % order.full_name,
        "📞 <b>Telefon:</b> %s" % order.phone,
    ]
    if order.telegram_username:
        uname = order.telegram_username.lstrip("@")
        lines.append("💬 <b>Telegram:</b> @%s" % uname)
    if order.message:
        lines.append("📝 <b>Izoh:</b> %s" % order.message)

    lines.append("")
    lines.append("<b>Mahsulotlar:</b>")
    for item in order.items.all():
        lines.append(
            f"• {item.product_name} ({item.variant_label}) — "
            f"{item.quantity} x ${item.product_price} = ${item.subtotal}"
        )

    lines.append("")
    lines.append(f"💰 <b>Jami:</b> ${order.total_price}")

    text = "\n".join(lines)

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=8,
        )
        resp.raise_for_status()

        # Best-effort: also send the first product's photo, if available.
        first_item = order.items.select_related("product").first()
        if first_item and first_item.product and first_item.product.image:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data={"chat_id": chat_id, "caption": f"Buyurtma #{order.pk}"},
                    files={"photo": first_item.product.image.open("rb")},
                    timeout=10,
                )
            except Exception:
                logger.exception("Buyurtma rasmi Telegramga yuborilmadi")

        order.telegram_notified = True
        order.save(update_fields=["telegram_notified"])
        return True
    except Exception:
        logger.exception("Telegramga buyurtma xabarini yuborishda xatolik")
        return False
