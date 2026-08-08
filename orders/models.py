from django.db import models
from shop.models import Product


class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_SHIPPED = "shipped"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_NEW, "Yangi / Новый"),
        (STATUS_CONFIRMED, "Tasdiqlangan / Подтверждён"),
        (STATUS_SHIPPED, "Yuborilgan / Отправлен"),
        (STATUS_DONE, "Bajarilgan / Выполнен"),
        (STATUS_CANCELLED, "Bekor qilingan / Отменён"),
    ]

    full_name = models.CharField("Ism familiya", max_length=150)
    phone = models.CharField("Telefon raqam", max_length=32)
    telegram_username = models.CharField("Telegram username", max_length=64, blank=True)
    message = models.TextField("Xabar / Izoh", blank=True)

    status = models.CharField("Holati", max_length=15, choices=STATUS_CHOICES, default=STATUS_NEW)
    total_price = models.DecimalField("Jami summa ($)", max_digits=10, decimal_places=2, default=0)

    telegram_notified = models.BooleanField("Telegramga yuborildi", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.full_name}"

    def recalc_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.SET_NULL, null=True)

    product_name = models.CharField("Mahsulot nomi", max_length=150)
    product_price = models.DecimalField("Narxi ($)", max_digits=10, decimal_places=2)
    variant_label = models.CharField("Tanlangan hajm", max_length=50, default="To'liq flakon")
    variant_volume_ml = models.PositiveIntegerField("Hajm (ml)", blank=True, null=True)
    quantity = models.PositiveIntegerField("Soni", default=1)

    class Meta:
        verbose_name = "Buyurtma tarkibi"
        verbose_name_plural = "Buyurtma tarkiblari"

    def __str__(self):
        return f"{self.product_name} ({self.variant_label}) x{self.quantity}"

    @property
    def subtotal(self):
        return self.product_price * self.quantity
