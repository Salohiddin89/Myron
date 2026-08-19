from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("product/<slug:slug>/vote/", views.product_vote, name="product_vote"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("delivery-terms/", views.delivery_terms, name="delivery_terms"),
]
