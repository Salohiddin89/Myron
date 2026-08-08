from django.conf import settings


def cart_context(request):
    cart = request.session.get(settings.CART_SESSION_ID, {})
    count = 0
    for item in cart.values():
        try:
            if isinstance(item, dict):
                count += int(item.get("quantity", 0))
            else:
                count += int(item)
        except (TypeError, ValueError):
            continue
    return {"cart_count": count}


def site_context(request):
    try:
        from shop.models import SiteSettings
        s = SiteSettings.get_settings()
        return {
            "SITE_NAME": s.site_name or settings.SITE_NAME,
            "SITE_PHONE": s.phone or settings.SITE_PHONE,
            "SITE_EMAIL": getattr(settings, "SITE_EMAIL", "info@MYRON.uz"),
            "SITE_ADDRESS_UZ": getattr(settings, "SITE_ADDRESS_UZ", "Toshkent sh."),
            "SITE_ADDRESS_RU": getattr(settings, "SITE_ADDRESS_RU", "г. Ташкент"),
            "SITE_INSTAGRAM": s.instagram_url or settings.SITE_INSTAGRAM,
            "SITE_TELEGRAM": s.telegram_url or settings.SITE_TELEGRAM,
            "site_settings": s,
        }
    except Exception:
        return {
            "SITE_NAME": settings.SITE_NAME,
            "SITE_PHONE": settings.SITE_PHONE,
            "SITE_EMAIL": getattr(settings, "SITE_EMAIL", "info@MYRON.uz"),
            "SITE_ADDRESS_UZ": getattr(settings, "SITE_ADDRESS_UZ", "Toshkent sh."),
            "SITE_ADDRESS_RU": getattr(settings, "SITE_ADDRESS_RU", "г. Ташкент"),
            "SITE_INSTAGRAM": settings.SITE_INSTAGRAM,
            "SITE_TELEGRAM": settings.SITE_TELEGRAM,
            "site_settings": None,
        }
