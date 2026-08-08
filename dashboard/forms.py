from django import forms

from orders.models import Order
from shop.models import Product, SiteSettings


class StaffLoginForm(forms.Form):
    username = forms.CharField(label="Login", max_length=150)
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name_uz",
            "name_ru",
            "slug",
            "brand",
            "gender",
            "concentration",
            "volume_ml",
            "price",
            "old_price",
            "sell_by_ml",
            "price_10ml",
            "price_20ml",
            "price_30ml",
            "price_40ml",
            "price_50ml",
            "image",
            "image_2",
            "short_description_uz",
            "short_description_ru",
            "description_uz",
            "description_ru",
            "composition_uz",
            "composition_ru",
            "rating",
            "reviews_count",
            "stock",
            "is_new",
            "is_bestseller",
            "is_active",
        ]
        widgets = {
            "description_uz": forms.Textarea(attrs={"rows": 4}),
            "description_ru": forms.Textarea(attrs={"rows": 4}),
            "composition_uz": forms.Textarea(attrs={"rows": 3}),
            "composition_ru": forms.Textarea(attrs={"rows": 3}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "phone",
            "instagram_url",
            "telegram_url",
            "hero_image",
            "about_image_1",
            "about_image_2",
        ]
