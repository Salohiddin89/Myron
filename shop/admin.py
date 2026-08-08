from django.contrib import admin
from django.utils.html import format_html
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
        ("Asosiy ma'lumot", {
            "fields": (("name_uz", "name_ru"), "slug", "brand", ("gender", "concentration"), "volume_ml")
        }),
        ("Narx va ombor", {
            "fields": (
                ("price", "old_price"),
                "sell_by_ml",
                ("price_10ml", "price_20ml", "price_30ml", "price_40ml", "price_50ml"),
                "stock",
            )
        }),
        ("Rasmlar", {
            "fields": ("image", "image_2")
        }),
        ("Qisqa tavsif", {
            "fields": (("short_description_uz", "short_description_ru"),)
        }),
        ("To'liq tavsif", {
            "fields": (("description_uz", "description_ru"),)
        }),
        ("Tarkibi / Состав", {
            "fields": (("composition_uz", "composition_ru"),)
        }),
        ("Reyting va holat", {
            "fields": (("rating", "reviews_count"), ("is_new", "is_bestseller", "is_active"))
        }),
    )

    @admin.display(description="Rasm")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:46px;height:46px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"
