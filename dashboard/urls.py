from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("kirish/", views.dashboard_login, name="login"),
    path("chiqish/", views.dashboard_logout, name="logout"),
    path("tahlil/", views.analytics_view, name="analytics"),
    path("mahsulotlar/", views.product_list, name="product_list"),
    path("mahsulotlar/yangi/", views.product_create, name="product_create"),
    path("mahsulotlar/<int:pk>/tahrirlash/", views.product_update, name="product_update"),
    path("mahsulotlar/<int:pk>/holat/", views.product_toggle_active, name="product_toggle_active"),
    path("mahsulotlar/<int:pk>/ochirish/", views.product_delete, name="product_delete"),
    path("buyurtmalar/", views.order_list, name="order_list"),
    path("buyurtmalar/<int:pk>/", views.order_detail, name="order_detail"),
    path("buyurtmalar/<int:pk>/status-otkazish/", views.order_quick_status, name="order_quick_status"),
    path("buyurtmalar/<int:pk>/chek/", views.order_receipt, name="order_receipt"),
    path("sozlamalar/", views.site_settings_view, name="settings"),
]
