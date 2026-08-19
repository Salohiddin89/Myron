from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "thumb", "name_uz", "brand", "gender", "concentration",
        "price", "sell_by_ml", "old_price", "stock", "is_new", "is_bestseller", "is_active",
    )
    list_display_links = ("thumb", "name_uz")
    list_filter = ("gender", "concentration", "is_new", "is_bestseller", "is_active")
    search_fields = ("name_uz", "name_ru", "brand")
    prepopulated_fields = {"slug": ("name_uz",)}
    list_editable = ("price", "stock", "is_new", "is_bestseller", "is_active")
    inlines = [ProductImageInline]

    fieldsets = (
        (_("Asosiy ma'lumot"), {
            "fields": (("name_uz", "name_ru"), "slug", "brand", ("gender", "concentration"), "volume_ml")
        }),
        (_("Narx va ombor"), {
            "fields": (
                ("price", "old_price"),
                "sell_by_ml",
                ("price_10ml", "price_20ml", "price_30ml", "price_40ml", "price_50ml"),
                "stock",
            )
        }),
        (_("Rasmlar"), {
            "fields": ("image", "box_image", "image_2")
        }),
        (_("Qisqa tavsif"), {
            "fields": (("short_description_uz", "short_description_ru"),)
        }),
        (_("To'liq tavsif"), {
            "fields": (("description_uz", "description_ru"),)
        }),
        (_("Tarkibi / Sostav"), {
            "fields": (("composition_uz", "composition_ru"),)
        }),
        (_("Aromat notalari"), {
            "fields": (
                ("top_notes_uz", "top_notes_ru"),
                ("heart_notes_uz", "heart_notes_ru"),
                ("base_notes_uz", "base_notes_ru"),
            )
        }),
        (_("Reyting va holat"), {
            "fields": (
                ("rating", "reviews_count"),
                ("show_user_rating", "show_when_to_wear"),
                ("is_new", "is_bestseller", "is_active"),
            )
        }),
    )

    @admin.display(description=_("Rasm"))
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:46px;height:46px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"
