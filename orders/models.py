from django.db import models
from django.utils.translation import gettext_lazy as _
from shop.models import Product


class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_SHIPPED = "shipped"
    STATUS_DONE = "done"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_NEW, _("Yangi")),
        (STATUS_CONFIRMED, _("Tasdiqlangan")),
        (STATUS_SHIPPED, _("Yuborilgan")),
        (STATUS_DONE, _("Bajarilgan")),
        (STATUS_CANCELLED, _("Bekor qilingan")),
    ]

    full_name = models.CharField(_("Ism familiya"), max_length=150)
    phone = models.CharField(_("Telefon raqam"), max_length=32)
    telegram_username = models.CharField(_("Telegram username"), max_length=64, blank=True)
    message = models.TextField(_("Xabar / Izoh"), blank=True)

    status = models.CharField(_("Holati"), max_length=15, choices=STATUS_CHOICES, default=STATUS_NEW)
    total_price = models.DecimalField(_("Jami summa ($)"), max_digits=10, decimal_places=2, default=0)

    telegram_notified = models.BooleanField(_("Telegramga yuborildi"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{_('Buyurtma')} #{self.pk} — {self.full_name}"

    def recalc_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.SET_NULL, null=True)

    product_name = models.CharField(_("Mahsulot nomi"), max_length=150)
    product_price = models.DecimalField(_("Narxi ($)"), max_digits=10, decimal_places=2)
    variant_label = models.CharField(_("Tanlangan hajm"), max_length=50, default=_("To'liq flakon"))
    variant_volume_ml = models.PositiveIntegerField(_("Hajm (ml)"), blank=True, null=True)
    quantity = models.PositiveIntegerField(_("Soni"), default=1)

    class Meta:
        verbose_name = _("Buyurtma tarkibi")
        verbose_name_plural = _("Buyurtma tarkiblari")

    def __str__(self):
        return f"{self.product_name} ({self.variant_label}) x{self.quantity}"

    @property
    def subtotal(self):
        return self.product_price * self.quantity
