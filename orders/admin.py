from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "variant_label", "product_price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "phone", "telegram_username",
        "total_price", "status", "telegram_notified", "created_at",
    )
    list_display_links = ("id", "full_name")
    list_filter = ("status", "telegram_notified", "created_at")
    search_fields = ("full_name", "phone", "telegram_username")
    list_editable = ("status",)
    readonly_fields = ("total_price", "telegram_notified", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Mijoz", {"fields": (("full_name", "phone"), "telegram_username", "message")}),
        ("Buyurtma holati", {"fields": (("status", "total_price"), "telegram_notified")}),
        ("Vaqt", {"fields": (("created_at", "updated_at"),)}),
    )
