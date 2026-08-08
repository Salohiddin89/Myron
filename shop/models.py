import os
import stat

from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import get_language


def _clear_readonly_and_unlock(file_field):
    if not file_field:
        return

    try:
        file_path = file_field.storage.path(file_field.name)
    except (AttributeError, ValueError, OSError):
        return

    if not file_path or not os.path.exists(file_path):
        return

    try:
        current_mode = os.stat(file_path).st_mode
        os.chmod(file_path, current_mode | stat.S_IWRITE)
    except OSError:
        pass


def _remove_existing_file(path):
    if not path or not os.path.exists(path):
        return
    try:
        current_mode = os.stat(path).st_mode
        os.chmod(path, current_mode | stat.S_IWRITE)
        os.remove(path)
    except OSError:
        pass


def _safe_image_url(image_field, fallback_path="shop/img/product-placeholder.png"):
    if not image_field or not getattr(image_field, "name", None):
        return static(fallback_path)

    try:
        if getattr(image_field, "storage", None) and image_field.storage.exists(
            image_field.name
        ):
            return image_field.url
    except (AttributeError, OSError, ValueError):
        pass

    # If image field has a valid name string, return its URL
    if getattr(image_field, "name", None) and str(image_field.name).strip():
        try:
            return image_field.url
        except (AttributeError, ValueError):
            pass

    return static(fallback_path)


class Product(models.Model):
    GENDER_WOMEN = "women"
    GENDER_MEN = "men"
    GENDER_UNISEX = "unisex"
    GENDER_CHOICES = [
        (GENDER_WOMEN, "Ayollar / Женский"),
        (GENDER_MEN, "Erkaklar / Мужской"),
        (GENDER_UNISEX, "Unisex / Унисекс"),
    ]
    GENDER_LABELS_UZ = {
        GENDER_WOMEN: "Ayollar",
        GENDER_MEN: "Erkaklar",
        GENDER_UNISEX: "Unisex",
    }
    GENDER_LABELS_RU = {
        GENDER_WOMEN: "Женский",
        GENDER_MEN: "Мужской",
        GENDER_UNISEX: "Унисекс",
    }

    CONCENTRATION_PARFUM = "parfum"
    CONCENTRATION_EDP = "edp"
    CONCENTRATION_EDT = "edt"
    CONCENTRATION_EDC = "edc"
    CONCENTRATION_CHOICES = [
        (CONCENTRATION_PARFUM, "Extrait de Parfum"),
        (CONCENTRATION_EDP, "Eau de Parfum"),
        (CONCENTRATION_EDT, "Eau de Toilette"),
        (CONCENTRATION_EDC, "Eau de Cologne"),
    ]
    CONCENTRATION_LABELS_UZ = {
        CONCENTRATION_PARFUM: "Parfyum ekstrakti",
        CONCENTRATION_EDP: "Parfyum suvi",
        CONCENTRATION_EDT: "Tualet suvi",
        CONCENTRATION_EDC: "Odekolon",
    }
    CONCENTRATION_LABELS_RU = {
        CONCENTRATION_PARFUM: "Экстракт духов",
        CONCENTRATION_EDP: "Парфюмерная вода",
        CONCENTRATION_EDT: "Туалетная вода",
        CONCENTRATION_EDC: "Одеколон",
    }

    slug = models.SlugField(max_length=160, unique=True, blank=True)

    name_uz = models.CharField("Nomi (UZ)", max_length=150)
    name_ru = models.CharField("Название (RU)", max_length=150, blank=True)

    brand = models.CharField("Brend", max_length=100, default="MYRON", blank=True)

    gender = models.CharField(
        "Toifa", max_length=10, choices=GENDER_CHOICES, default=GENDER_UNISEX
    )
    concentration = models.CharField(
        "Konsentratsiya",
        max_length=10,
        choices=CONCENTRATION_CHOICES,
        default=CONCENTRATION_EDP,
    )

    volume_ml = models.PositiveIntegerField("Hajmi (ml)", default=50)

    price = models.DecimalField("Narxi ($)", max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        "Eski narxi ($)", max_digits=10, decimal_places=2, blank=True, null=True
    )
    sell_by_ml = models.BooleanField("Ml bo'yicha sotiladi", default=False)
    price_10ml = models.DecimalField(
        "10 ml narxi ($)", max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_20ml = models.DecimalField(
        "20 ml narxi ($)", max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_30ml = models.DecimalField(
        "30 ml narxi ($)", max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_40ml = models.DecimalField(
        "40 ml narxi ($)", max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_50ml = models.DecimalField(
        "50 ml narxi ($)", max_digits=10, decimal_places=2, blank=True, null=True
    )

    image = models.ImageField("Asosiy rasm", upload_to="products/")
    image_2 = models.ImageField(
        "Qo'shimcha rasm", upload_to="products/", blank=True, null=True
    )

    short_description_uz = models.CharField(
        "Qisqa tavsif (UZ)", max_length=220, blank=True
    )
    short_description_ru = models.CharField(
        "Краткое описание (RU)", max_length=220, blank=True
    )

    description_uz = models.TextField("To'liq tavsif (UZ)", blank=True)
    description_ru = models.TextField("Полное описание (RU)", blank=True)

    composition_uz = models.TextField(
        "Tarkibi / sastavi (UZ)",
        blank=True,
        help_text="Masalan: Bergamot, Yosemik yog'och, Amber, Musk",
    )
    composition_ru = models.TextField("Состав (RU)", blank=True)

    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=5.0)
    reviews_count = models.PositiveIntegerField("Sharhlar soni", default=0)

    is_new = models.BooleanField("Yangi mahsulot", default=False)
    is_bestseller = models.BooleanField("Ko'p sotilgan", default=False)
    is_active = models.BooleanField("Faol (saytda ko'rinadi)", default=True)
    stock = models.PositiveIntegerField("Ombordagi soni", default=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Atir / Parfyum"
        verbose_name_plural = "Atirlar / Parfyумлар"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(self.name_uz) or slugify(self.name_ru) or "product"
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})

    @property
    def image_url(self):
        return _safe_image_url(self.image)

    @property
    def image_2_url(self):
        return _safe_image_url(self.image_2)

    @property
    def name(self):
        return self.name_ru if get_language() == "ru" and self.name_ru else self.name_uz

    @property
    def short_description(self):
        if get_language() == "ru" and self.short_description_ru:
            return self.short_description_ru
        return self.short_description_uz

    @property
    def description(self):
        if get_language() == "ru" and self.description_ru:
            return self.description_ru
        return self.description_uz

    @property
    def composition(self):
        if get_language() == "ru" and self.composition_ru:
            return self.composition_ru
        return self.composition_uz

    @property
    def gender_label(self):
        return self.gender_label_for(self.gender)

    @classmethod
    def gender_label_for(cls, code):
        if get_language() == "ru":
            return cls.GENDER_LABELS_RU.get(code, code)
        return cls.GENDER_LABELS_UZ.get(code, code)

    @property
    def concentration_label(self):
        return self.concentration_label_for(self.concentration)

    @classmethod
    def concentration_label_for(cls, code):
        if get_language() == "ru":
            return cls.CONCENTRATION_LABELS_RU.get(code, code)
        return cls.CONCENTRATION_LABELS_UZ.get(code, code)

    @classmethod
    def get_concentration_choices_localized(cls):
        return [
            (code, cls.concentration_label_for(code))
            for code, _ in cls.CONCENTRATION_CHOICES
        ]

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(round((self.old_price - self.price) / self.old_price * 100))
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def full_variant_label(self):
        return f"To'liq flakon ({self.volume_ml} ml)"

    @property
    def purchase_variants(self):
        variants = [
            {
                "code": "full",
                "label": self.full_variant_label,
                "price": self.price,
                "volume_ml": self.volume_ml,
            }
        ]
        if self.sell_by_ml:
            for volume, price in self.ml_price_pairs:
                if price:
                    variants.append(
                        {
                            "code": str(volume),
                            "label": f"{volume} ml",
                            "price": price,
                            "volume_ml": volume,
                        }
                    )
        return variants

    @property
    def ml_price_pairs(self):
        return [
            (10, self.price_10ml),
            (20, self.price_20ml),
            (30, self.price_30ml),
            (40, self.price_40ml),
            (50, self.price_50ml),
        ]

    def get_variant(self, code):
        code = str(code or "full")
        for variant in self.purchase_variants:
            if variant["code"] == code:
                return variant
        return self.purchase_variants[0]


class ProductImage(models.Model):
    """Optional extra gallery images for a product."""

    product = models.ForeignKey(
        Product, related_name="gallery", on_delete=models.CASCADE
    )
    image = models.ImageField("Rasm", upload_to="products/gallery/")

    @property
    def image_url(self):
        return _safe_image_url(self.image)

    class Meta:
        verbose_name = "Qo'shimcha rasm"
        verbose_name_plural = "Qo'shimcha rasmlar"

    def __str__(self):
        return f"{self.product.name_uz} rasmi"


class SiteSettings(models.Model):
    site_name = models.CharField("Sayt nomi", max_length=100, default="MYRON")
    phone = models.CharField(
        "Telefon raqami", max_length=50, default="+998 90 123 45 67"
    )
    instagram_url = models.URLField(
        "Instagram havola", default="https://instagram.com/myron_perfume", blank=True
    )
    telegram_url = models.URLField(
        "Telegram havola", default="https://t.me/myron_perfume", blank=True
    )

    hero_image = models.ImageField(
        "Bosh sahifa rasmi (Hero)", upload_to="site/", blank=True, null=True
    )
    about_image_1 = models.ImageField(
        "Biz haqimizda 1-rasm", upload_to="site/", blank=True, null=True
    )
    about_image_2 = models.ImageField(
        "Biz haqimizda 2-rasm", upload_to="site/", blank=True, null=True
    )

    class Meta:
        verbose_name = "Sayt Sozlamalari"
        verbose_name_plural = "Sayt Sozlamalari"

    def __str__(self):
        return "Sayt Sozlamalari"

    def save(self, *args, **kwargs):
        for field_name in ["hero_image", "about_image_1", "about_image_2"]:
            current_field = getattr(self, field_name, None)
            if not current_field or not getattr(current_field, "name", None):
                continue

            old_value = None
            if self.pk:
                try:
                    old_value = (
                        self.__class__.objects.filter(pk=self.pk)
                        .values_list(field_name, flat=True)
                        .first()
                    )
                except Exception:
                    old_value = None

            if old_value and old_value == current_field.name:
                try:
                    old_path = current_field.storage.path(current_field.name)
                    _remove_existing_file(old_path)
                except (AttributeError, OSError, ValueError):
                    pass

            try:
                file_path = current_field.storage.path(current_field.name)
                _remove_existing_file(file_path)
            except (AttributeError, OSError, ValueError):
                pass

        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
