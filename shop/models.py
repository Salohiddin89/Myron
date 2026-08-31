import os
import re
import stat

from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import get_language, gettext, gettext_lazy as _


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

    try:
        if hasattr(image_field, "path") and os.path.exists(image_field.path):
            return image_field.url
    except (AttributeError, OSError, ValueError):
        pass

    return static(fallback_path)



class Product(models.Model):
    VOTE_TYPE_RATING = "rating"
    VOTE_TYPE_WEAR = "wear"
    RATING_VOTE_CHOICES = (
        ("love", _("Love")),
        ("like", _("Like")),
        ("ok", _("OK")),
        ("dislike", _("Dislike")),
        ("hate", _("Hate")),
    )
    WEAR_VOTE_CHOICES = (
        ("winter", _("Winter")),
        ("spring", _("Spring")),
        ("summer", _("Summer")),
        ("fall", _("Fall")),
        ("day", _("Day")),
        ("night", _("Night")),
    )

    GENDER_WOMEN = "women"
    GENDER_MEN = "men"
    GENDER_UNISEX = "unisex"
    GENDER_CHOICES = [
        (GENDER_WOMEN, _("Ayollar")),
        (GENDER_MEN, _("Erkaklar")),
        (GENDER_UNISEX, _("Unisex")),
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
        (CONCENTRATION_PARFUM, _("Parfyum ekstrakti")),
        (CONCENTRATION_EDP, _("Parfyum suvi")),
        (CONCENTRATION_EDT, _("Tualet suvi")),
        (CONCENTRATION_EDC, _("Odekolon")),
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

    name_uz = models.CharField(_("Nomi (UZ)"), max_length=150)
    name_ru = models.CharField(_("Название (RU)"), max_length=150, blank=True)

    brand = models.CharField(_("Brend"), max_length=100, default="MYRON", blank=True)

    gender = models.CharField(
        _("Toifa"), max_length=10, choices=GENDER_CHOICES, default=GENDER_UNISEX
    )
    concentration = models.CharField(
        _("Konsentratsiya"),
        max_length=10,
        choices=CONCENTRATION_CHOICES,
        default=CONCENTRATION_EDP,
    )

    volume_ml = models.PositiveIntegerField(_("Hajmi (ml)"), default=50)

    price = models.DecimalField(_("Narxi ($)"), max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        _("Eski narxi ($)"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    sell_by_ml = models.BooleanField(_("Ml bo'yicha sotiladi"), default=False)
    price_10ml = models.DecimalField(
        _("10 ml narxi ($)"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_20ml = models.DecimalField(
        _("20 ml narxi ($)"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_30ml = models.DecimalField(
        _("30 ml narxi ($)"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_40ml = models.DecimalField(
        _("40 ml narxi ($)"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    price_50ml = models.DecimalField(
        _("50 ml narxi ($)"), max_digits=10, decimal_places=2, blank=True, null=True
    )

    image = models.ImageField(_("Asosiy rasm"), upload_to="products/", blank=True, null=True)
    box_image = models.ImageField(
        _("Karobka rasmi"),
        upload_to="products/boxes/",
        blank=True,
        null=True,
        help_text=_("Kursor mahsulot ustiga kelganda ko'rsatiladigan karobka rasmi."),
    )
    image_2 = models.ImageField(
        _("Qo'shimcha rasm"), upload_to="products/", blank=True, null=True
    )

    short_description_uz = models.CharField(
        _("Qisqa tavsif (UZ)"), max_length=220, blank=True
    )
    short_description_ru = models.CharField(
        _("Краткое описание (RU)"), max_length=220, blank=True
    )

    description_uz = models.TextField(_("To'liq tavsif (UZ)"), blank=True)
    description_ru = models.TextField(_("Полное описание (RU)"), blank=True)

    composition_uz = models.TextField(
        _("Tarkibi / sastavi (UZ)"),
        blank=True,
        help_text=_("Masalan: Bergamot, Yosemik yog'och, Amber, Musk"),
    )
    composition_ru = models.TextField(_("Состав (RU)"), blank=True)

    top_notes_uz = models.TextField(
        _("Yuqori nota (UZ)"),
        blank=True,
        help_text=_("Masalan: Bergamot, limon, pushti murch. Vergul yoki yangi qatorda yozing."),
    )
    top_notes_ru = models.TextField(_("Верхняя нота (RU)"), blank=True)
    heart_notes_uz = models.TextField(
        _("O'rta nota (UZ)"),
        blank=True,
        help_text=_("Masalan: Atirgul, yasmin, dolchin. Vergul yoki yangi qatorda yozing."),
    )
    heart_notes_ru = models.TextField(_("Средняя нота (RU)"), blank=True)
    base_notes_uz = models.TextField(
        _("Bazaviy nota (UZ)"),
        blank=True,
        help_text=_("Masalan: Vanil, amber, mushk. Vergul yoki yangi qatorda yozing."),
    )
    base_notes_ru = models.TextField(_("Базовая нота (RU)"), blank=True)

    rating = models.DecimalField(_("Reyting"), max_digits=2, decimal_places=1, default=5.0, blank=True)
    reviews_count = models.PositiveIntegerField(_("Sharhlar soni"), default=0, blank=True)

    is_new = models.BooleanField(_("Yangi mahsulot"), default=False)
    is_bestseller = models.BooleanField(_("Ko'p sotilgan"), default=False)
    show_user_rating = models.BooleanField(
        _("Foydalanuvchi reytingi blokini ko'rsatish"), default=True
    )
    show_when_to_wear = models.BooleanField(
        _("Qachon foydalanish blokini ko'rsatish"), default=True
    )
    is_active = models.BooleanField(_("Faol (saytda ko'rinadi)"), default=True)
    stock = models.PositiveIntegerField(_("Ombordagi soni"), default=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Atir / Parfyum")
        verbose_name_plural = _("Atirlar / Parfyumlar")
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
    def box_image_url(self):
        return _safe_image_url(self.box_image)

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
    def top_notes(self):
        if get_language() == "ru" and self.top_notes_ru:
            return self.top_notes_ru
        return self.top_notes_uz

    @property
    def heart_notes(self):
        if get_language() == "ru" and self.heart_notes_ru:
            return self.heart_notes_ru
        return self.heart_notes_uz

    @property
    def base_notes(self):
        if get_language() == "ru" and self.base_notes_ru:
            return self.base_notes_ru
        return self.base_notes_uz

    @staticmethod
    def _split_note_items(value):
        return [
            item.strip()
            for item in re.split(r"[,;\n]+", value or "")
            if item.strip()
        ]

    @property
    def top_note_items(self):
        return self._split_note_items(self.top_notes)

    @property
    def heart_note_items(self):
        return self._split_note_items(self.heart_notes)

    @property
    def base_note_items(self):
        return self._split_note_items(self.base_notes)

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
        label = gettext("To'liq flakon")
        return f"{label} ({self.volume_ml} ml)"

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


class ProductVote(models.Model):
    product = models.ForeignKey(
        Product, related_name="votes", on_delete=models.CASCADE
    )
    visitor_key = models.CharField(max_length=128)
    vote_type = models.CharField(
        max_length=12,
        choices=(
            (Product.VOTE_TYPE_RATING, _("User Rating")),
            (Product.VOTE_TYPE_WEAR, _("When to wear")),
        ),
    )
    choice = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("product", "visitor_key", "vote_type"),
                name="unique_product_vote_visitor_type",
            )
        ]
        indexes = [
            models.Index(
                fields=("product", "vote_type", "choice"),
                name="shop_product_vote_lookup_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product.name_uz}: {self.vote_type}/{self.choice}"


class ProductImage(models.Model):
    """Optional extra gallery images for a product."""

    product = models.ForeignKey(
        Product, related_name="gallery", on_delete=models.CASCADE
    )
    image = models.ImageField(_("Rasm"), upload_to="products/gallery/")

    @property
    def image_url(self):
        return _safe_image_url(self.image)

    class Meta:
        verbose_name = _("Qo'shimcha rasm")
        verbose_name_plural = _("Qo'shimcha rasmlar")

    def __str__(self):
        return f"{self.product.name_uz} rasmi"


class SiteSettings(models.Model):
    site_name = models.CharField(_("Sayt nomi"), max_length=100, default="MYRON", blank=True)
    phone = models.CharField(
        _("Telefon raqami"), max_length=50, default="+998 90 123 45 67", blank=True
    )
    instagram_url = models.URLField(
        _("Instagram havola"), default="https://instagram.com/myron_perfume", blank=True
    )
    telegram_url = models.URLField(
        _("Telegram havola"), default="https://t.me/myron_perfume", blank=True
    )

    hero_image = models.ImageField(
        _("Bosh sahifa rasmi (Hero)"), upload_to="site/", blank=True, null=True
    )
    about_image_1 = models.ImageField(
        _("Biz haqimizda 1-rasm"), upload_to="site/", blank=True, null=True
    )
    about_image_2 = models.ImageField(
        _("Biz haqimizda 2-rasm"), upload_to="site/", blank=True, null=True
    )

    # Biz haqimizda sarlavha va matni
    about_title_uz = models.CharField(
        _("Biz haqimizda sarlavha (UZ)"),
        max_length=200,
        default="NOZIK ATIRLAR SAN'ATI",
        blank=True,
    )
    about_title_ru = models.CharField(
        _("Biz haqimizda sarlavha (RU)"),
        max_length=200,
        default="ИСКУССТВО ИЗЫСКАННЫХ АРОМАТОВ",
        blank=True,
    )

    about_text_uz = models.TextField(
        _("Biz haqimizda matn (UZ)"),
        default="MYRON'da biz atir shunchaki hid emas — u bir bayonot, bir hissiyot, bir xotira ekaniga ishonamiz. Bizning atirlarimiz dunyoning eng sara ingredientlaridan mohir parfyumerlar tomonidan tayyorlanadi, sizga tengsiz sifat va nafosat bag'ishlaydi.",
        blank=True,
    )
    about_text_ru = models.TextField(
        _("Biz haqimizda matn (RU)"),
        default="В MYRON мы верим, что духи — это не просто аромат, это заявление, эмоция и воспоминание. Наши ароматы создаются опытными парфюмерами из лучших мировых ингредиентов.",
        blank=True,
    )

    # 4 ta xususiyat bloki (Emoji, sarlavha, matn)
    # 1-xususiyat
    about_feature1_icon = models.CharField(
        _("1-xususiyat emojisi"), max_length=20, default="🌿", blank=True
    )
    about_feature1_title_uz = models.CharField(
        _("1-xususiyat sarlavha (UZ)"), max_length=150, default="SIFATLI TARKIB", blank=True
    )
    about_feature1_title_ru = models.CharField(
        _("1-xususiyat sarlavha (RU)"), max_length=150, default="Качественный состав", blank=True
    )
    about_feature1_text_uz = models.CharField(
        _("1-xususiyat matn (UZ)"), max_length=255, default="Dunyoning eng sara joylaridan yetkazilgan", blank=True
    )
    about_feature1_text_ru = models.CharField(
        _("1-xususiyat matn (RU)"), max_length=255, default="Собрано из лучших уголков мира", blank=True
    )

    # 2-xususiyat
    about_feature2_icon = models.CharField(
        _("2-xususiyat emojisi"), max_length=20, default="🎓", blank=True
    )
    about_feature2_title_uz = models.CharField(
        _("2-xususiyat sarlavha (UZ)"), max_length=150, default="MOHIR USTALAR", blank=True
    )
    about_feature2_title_ru = models.CharField(
        _("2-xususiyat sarlavha (RU)"), max_length=150, default="Опытные парфюмеры", blank=True
    )
    about_feature2_text_uz = models.CharField(
        _("2-xususiyat matn (UZ)"), max_length=255, default="Professional parfyumerlar tomonidan yaratilgan", blank=True
    )
    about_feature2_text_ru = models.CharField(
        _("2-xususiyat matn (RU)"), max_length=255, default="Создано профессиональными парфюмерами", blank=True
    )

    # 3-xususiyat
    about_feature3_icon = models.CharField(
        _("3-xususiyat emojisi"), max_length=20, default="💎", blank=True
    )
    about_feature3_title_uz = models.CharField(
        _("3-xususiyat sarlavha (UZ)"), max_length=150, default="HASHAMATLI TAJRIBA", blank=True
    )
    about_feature3_title_ru = models.CharField(
        _("3-xususiyat sarlavha (RU)"), max_length=150, default="Роскошный опыт", blank=True
    )
    about_feature3_text_uz = models.CharField(
        _("3-xususiyat matn (UZ)"), max_length=255, default="Nafis qadoqlash va nozik detallar", blank=True
    )
    about_feature3_text_ru = models.CharField(
        _("3-xususiyat matn (RU)"), max_length=255, default="Изысканная упаковка и детали", blank=True
    )

    # 4-xususiyat
    about_feature4_icon = models.CharField(
        _("4-xususiyat emojisi"), max_length=20, default="🛡️", blank=True
    )
    about_feature4_title_uz = models.CharField(
        _("4-xususiyat sarlavha (UZ)"), max_length=150, default="KAFOLAT", blank=True
    )
    about_feature4_title_ru = models.CharField(
        _("4-xususiyat sarlavha (RU)"), max_length=150, default="Гарантия качества", blank=True
    )
    about_feature4_text_uz = models.CharField(
        _("4-xususiyat matn (UZ)"), max_length=255, default="100% originallik va sifat kafolati", blank=True
    )
    about_feature4_text_ru = models.CharField(
        _("4-xususiyat matn (RU)"), max_length=255, default="100% оригинальность и качество", blank=True
    )

    # Bosh sahifa (Hero) matnlari
    hero_title_uz = models.CharField(
        _("Hero sarlavha (UZ)"), max_length=255, default="MYRON PERFUME — HASHAMATLI PARFYUMERLAR UYI", blank=True
    )
    hero_title_ru = models.CharField(
        _("Hero sarlavha (RU)"), max_length=255, default="MYRON PERFUME — ДОМ ИЗЫСКАННОЙ ПАРФЮМЕРИИ", blank=True
    )
    hero_subtitle_uz = models.TextField(
        _("Hero ostki matn (UZ)"), default="Eng sara va eksklyuziv fransuz ingredientlaridan tayyorlangan nafis atirlar kolleksiyasi.", blank=True
    )
    hero_subtitle_ru = models.TextField(
        _("Hero ostki matn (RU)"), default="Коллекция утонченных ароматов, созданных из лучших французских ингредиентов.", blank=True
    )
    hero_btn_uz = models.CharField(
        _("Hero tugmasi matni (UZ)"), max_length=100, default="Katalogni ko'rish", blank=True
    )
    hero_btn_ru = models.CharField(
        _("Hero tugmasi matni (RU)"), max_length=100, default="Смотреть каталог", blank=True
    )

    # Biz haqimizda ostki sarlavha
    about_subtitle_uz = models.CharField(
        _("Biz haqimizda ostki matn (UZ)"), max_length=255, default="Har bir tomchida nozik did, yuqori sifat va takrorlanmas hissiyot aks etadi.", blank=True
    )
    about_subtitle_ru = models.CharField(
        _("Biz haqimizda ostki matn (RU)"), max_length=255, default="В каждой капле отражается изысканный вкус, высокое качество и эмоции.", blank=True
    )

    # Katalog va Boshqa bo'lim sarlavhalari
    catalog_title_uz = models.CharField(
        _("Katalog sarlavha (UZ)"), max_length=200, default="EKSKLYUZIV PARFYUMERIA", blank=True
    )
    catalog_title_ru = models.CharField(
        _("Katalog sarlavha (RU)"), max_length=200, default="ЭКСКЛЮЗИВНАЯ ПАРФЮМЕРИЯ", blank=True
    )
    catalog_subtitle_uz = models.CharField(
        _("Katalog ostki matn (UZ)"), max_length=255, default="O'zingizga mos unikal aromatlarni tanlang va buyurtma bering.", blank=True
    )
    catalog_subtitle_ru = models.CharField(
        _("Katalog ostki matn (RU)"), max_length=255, default="Выберите уникальный аромат и оформите быстрый заказ.", blank=True
    )

    # Kontakt va Footer matnlari
    contact_title_uz = models.CharField(
        _("Kontaktlar sarlavha (UZ)"), max_length=200, default="BIZ BILAN BOG'LANING", blank=True
    )
    contact_title_ru = models.CharField(
        _("Kontaktlar sarlavha (RU)"), max_length=200, default="СВЯЖИТЕСЬ С НАМИ", blank=True
    )
    contact_subtitle_uz = models.CharField(
        _("Kontaktlar ostki matn (UZ)"), max_length=255, default="Savollaringiz bormi? Bizga qo'ng'iroq qiling yoki ijtimoiy tarmoqlarda yozing.", blank=True
    )
    contact_subtitle_ru = models.CharField(
        _("Kontaktlar ostki matn (RU)"), max_length=255, default="Есть вопросы? Позвоните нам или напишите в социальных сетях.", blank=True
    )

    footer_text_uz = models.TextField(
        _("Footer matni (UZ)"), default="MYRON Perfume — Yuqori sifat va nafosat ramzi. Barcha huquqlar himoyalangan.", blank=True
    )
    footer_text_ru = models.TextField(
        _("Footer matni (RU)"), default="MYRON Perfume — Символ высокого качества и изысканности. Все права защищены.", blank=True
    )

    # Tugmalar matnlari
    btn_buy_uz = models.CharField(
        _("Sotib olish tugmasi (UZ)"), max_length=100, default="Xarid qilish", blank=True
    )
    btn_buy_ru = models.CharField(
        _("Sotib olish tugmasi (RU)"), max_length=100, default="Купить сейчас", blank=True
    )
    btn_details_uz = models.CharField(
        _("Batafsil tugmasi (UZ)"), max_length=100, default="Batafsil ma'lumot", blank=True
    )
    btn_details_ru = models.CharField(
        _("Batafsil tugmasi (RU)"), max_length=100, default="Подробнее", blank=True
    )

    class Meta:
        verbose_name = _("Sayt Sozlamalari")
        verbose_name_plural = _("Sayt Sozlamalari")


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

    @property
    def hero_image_url(self):
        return _safe_image_url(self.hero_image, "shop/img/hero-placeholder.png")

    @property
    def about_image_1_url(self):
        return _safe_image_url(self.about_image_1, "shop/img/about-1.png")

    @property
    def about_image_2_url(self):
        return _safe_image_url(self.about_image_2, "shop/img/about-2.png")

    @property
    def hero_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.hero_title_ru or self.hero_title_uz or "MYRON PERFUME — ДОМ ИЗЫСКАННОЙ ПАРФЮМЕРИИ"
        return self.hero_title_uz or self.hero_title_ru or "MYRON PERFUME — HASHAMATLI PARFYUMERLAR UYI"

    @property
    def hero_subtitle(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.hero_subtitle_ru or self.hero_subtitle_uz or "Коллекция утонченных ароматов, созданных из лучших французских ингредиентов."
        return self.hero_subtitle_uz or self.hero_subtitle_ru or "Eng sara va eksklyuziv fransuz ingredientlaridan tayyorlangan nafis atirlar kolleksiyasi."

    @property
    def hero_btn(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.hero_btn_ru or self.hero_btn_uz or "Смотреть каталог"
        return self.hero_btn_uz or self.hero_btn_ru or "Katalogni ko'rish"

    @property
    def about_subtitle(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_subtitle_ru or self.about_subtitle_uz or "В каждой капле отражается изысканный вкус, высокое качество и эмоции."
        return self.about_subtitle_uz or self.about_subtitle_ru or "Har bir tomchida nozik did, yuqori sifat va takrorlanmas hissiyot aks etadi."

    @property
    def catalog_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.catalog_title_ru or self.catalog_title_uz or "ЭКСКЛЮЗИВНАЯ ПАРФЮМЕРИЯ"
        return self.catalog_title_uz or self.catalog_title_ru or "EKSKLYUZIV PARFYUMERIA"

    @property
    def catalog_subtitle(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.catalog_subtitle_ru or self.catalog_subtitle_uz or "Выберите уникальный аромат и оформите быстрый заказ."
        return self.catalog_subtitle_uz or self.catalog_subtitle_ru or "O'zingizga mos unikal aromatlarni tanlang va buyurtma bering."

    @property
    def contact_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.contact_title_ru or self.contact_title_uz or "СВЯЖИТЕСЬ С НАМИ"
        return self.contact_title_uz or self.contact_title_ru or "BIZ BILAN BOG'LANING"

    @property
    def contact_subtitle(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.contact_subtitle_ru or self.contact_subtitle_uz or "Есть вопросы? Позвоните нам или напишите в социальных сетях."
        return self.contact_subtitle_uz or self.contact_subtitle_ru or "Savollaringiz bormi? Bizga qo'ng'iroq qiling yoki ijtimoiy tarmoqlarda yozing."

    @property
    def footer_text(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.footer_text_ru or self.footer_text_uz or "MYRON Perfume — Символ высокого качества и изысканности. Все права защищены."
        return self.footer_text_uz or self.footer_text_ru or "MYRON Perfume — Yuqori sifat va nafosat ramzi. Barcha huquqlar himoyalangan."

    @property
    def btn_buy(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.btn_buy_ru or self.btn_buy_uz or "Купить сейчас"
        return self.btn_buy_uz or self.btn_buy_ru or "Xarid qilish"

    @property
    def btn_details(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.btn_details_ru or self.btn_details_uz or "Подробнее"
        return self.btn_details_uz or self.btn_details_ru or "Batafsil ma'lumot"

    @property
    def about_title(self):

        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_title_ru or self.about_title_uz or "ИСКУССТВО ИЗЫСКАННЫХ АРОМАТОВ"
        return self.about_title_uz or self.about_title_ru or "NOZIK ATIRLAR SAN'ATI"

    @property
    def about_text(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return (
                self.about_text_ru
                or self.about_text_uz
                or "В MYRON мы верим, что духи — это не просто аромат, это заявление, эмоция и воспоминание. Наши ароматы создаются опытными парфюмерами из лучших мировых ингредиентов."
            )
        return (
            self.about_text_uz
            or self.about_text_ru
            or "MYRON'da biz atir shunchaki hid emas — u bir bayonot, bir hissiyot, bir xotira ekaniga ishonamiz. Bizning atirlarimiz dunyoning eng sara ingredientlaridan mohir parfyumerlar tomonidan tayyorlanadi, sizga tengsiz sifat va nafosat bag'ishlaydi."
        )

    @property
    def about_feature1_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature1_title_ru or self.about_feature1_title_uz or "Качественный состав"
        return self.about_feature1_title_uz or self.about_feature1_title_ru or "SIFATLI TARKIB"

    @property
    def about_feature1_text(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature1_text_ru or self.about_feature1_text_uz or "Собрано из лучших уголков мира"
        return self.about_feature1_text_uz or self.about_feature1_text_ru or "Dunyoning eng sara joylaridan yetkazilgan"

    @property
    def about_feature2_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature2_title_ru or self.about_feature2_title_uz or "Опытные парфюмеры"
        return self.about_feature2_title_uz or self.about_feature2_title_ru or "MOHIR USTALAR"

    @property
    def about_feature2_text(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature2_text_ru or self.about_feature2_text_uz or "Создано профессиональными парфюмерами"
        return self.about_feature2_text_uz or self.about_feature2_text_ru or "Professional parfyumerlar tomonidan yaratilgan"

    @property
    def about_feature3_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature3_title_ru or self.about_feature3_title_uz or "Роскошный опыт"
        return self.about_feature3_title_uz or self.about_feature3_title_ru or "HASHAMATLI TAJRIBA"

    @property
    def about_feature3_text(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature3_text_ru or self.about_feature3_text_uz or "Изысканная упаковка и детали"
        return self.about_feature3_text_uz or self.about_feature3_text_ru or "Nafis qadoqlash va nozik detallar"

    @property
    def about_feature4_title(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature4_title_ru or self.about_feature4_title_uz or "Гарантия качества"
        return self.about_feature4_title_uz or self.about_feature4_title_ru or "KAFOLAT"

    @property
    def about_feature4_text(self):
        lang = (get_language() or "uz")[:2].lower()
        if lang == "ru":
            return self.about_feature4_text_ru or self.about_feature4_text_uz or "100% оригинальность и качество"
        return self.about_feature4_text_uz or self.about_feature4_text_ru or "100% originallik va sifat kafolati"

    @property
    def about_features(self):
        return [
            {
                "icon": self.about_feature1_icon or "🌿",
                "title": self.about_feature1_title,
                "text": self.about_feature1_text,
            },
            {
                "icon": self.about_feature2_icon or "🎓",
                "title": self.about_feature2_title,
                "text": self.about_feature2_text,
            },
            {
                "icon": self.about_feature3_icon or "💎",
                "title": self.about_feature3_title,
                "text": self.about_feature3_text,
            },
            {
                "icon": self.about_feature4_icon or "🛡️",
                "title": self.about_feature4_title,
                "text": self.about_feature4_text,
            },
        ]


