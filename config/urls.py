from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from django.utils.translation import gettext_lazy as _

admin.site.site_header = _("MYRON - Boshqaruv paneli")
admin.site.site_title = _("MYRON Admin")
admin.site.index_title = _("Do'kon boshqaruvi")


def redirect_dashboard_alias(request, remaining=""):
    target = "/MYRON-control-9821/"
    if remaining:
        target += remaining
    return redirect(target, permanent=False)


urlpatterns = [
    path("MAYRON-control-9821/", redirect_dashboard_alias),
    path("MAYRON-control-9821/<path:remaining>", redirect_dashboard_alias),
    path("mayron-control-9821/", redirect_dashboard_alias),
    path("mayron-control-9821/<path:remaining>", redirect_dashboard_alias),
    path("MYRON-control-9821/", include("dashboard.urls", namespace="dashboard")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("", include("shop.urls", namespace="shop")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
