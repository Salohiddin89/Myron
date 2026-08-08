import io
import math
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from shop.models import Product

FONT_PATH = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"


def _font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


GOLD = (212, 175, 55)
GOLD_LIGHT = (240, 211, 133)
CREAM = (246, 241, 230)


def make_bottle_image(bg_tone, glass_color, size=(800, 1000), label=""):
    """Procedurally draw a stylised perfume-bottle placeholder image in the
    site's green/gold palette (no external assets, no copyrighted material)."""
    w, h = size
    img = Image.new("RGB", size, bg_tone)
    draw = ImageDraw.Draw(img)

    # soft radial vignette
    for i in range(0, 420, 4):
        alpha = int(60 * (1 - i / 420))
        c = tuple(min(255, ch + alpha // 3) for ch in bg_tone)
        draw.ellipse(
            [w / 2 - 260 + i * 0.3, h * 0.32 - 260 + i * 0.3, w / 2 + 260 - i * 0.3, h * 0.32 + 260 - i * 0.3],
            outline=c,
        )

    # bottle body
    body_w, body_h = 260, 380
    bx0, by0 = w / 2 - body_w / 2, h * 0.34
    bx1, by1 = w / 2 + body_w / 2, by0 + body_h
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=26, fill=glass_color, outline=GOLD, width=3)

    # highlight streak
    hi_x0 = bx0 + body_w * 0.18
    draw.rounded_rectangle([hi_x0, by0 + 20, hi_x0 + 22, by1 - 20], radius=10,
                            fill=tuple(min(255, c + 35) for c in glass_color))

    # label plate
    label_w, label_h = body_w * 0.72, 120
    lx0, ly0 = w / 2 - label_w / 2, by0 + body_h * 0.32
    draw.rounded_rectangle([lx0, ly0, lx0 + label_w, ly0 + label_h], radius=8,
                            outline=GOLD, width=2, fill=tuple(max(0, c - 8) for c in glass_color))
    f_brand = _font(30)
    f_sub = _font(14)
    text = "MYRON"
    tb = draw.textbbox((0, 0), text, font=f_brand)
    draw.text((w / 2 - (tb[2] - tb[0]) / 2, ly0 + 18), text, font=f_brand, fill=GOLD_LIGHT)
    sub = (label or "PARFUM").upper()
    tb2 = draw.textbbox((0, 0), sub, font=f_sub)
    draw.text((w / 2 - (tb2[2] - tb2[0]) / 2, ly0 + 62), sub, font=f_sub, fill=CREAM)

    # neck
    neck_w = 60
    draw.rectangle([w / 2 - neck_w / 2, by0 - 70, w / 2 + neck_w / 2, by0 + 6], fill=(30, 30, 30))

    # gold cap
    cap_w, cap_h = 100, 90
    draw.rounded_rectangle(
        [w / 2 - cap_w / 2, by0 - 70 - cap_h, w / 2 + cap_w / 2, by0 - 70 + 14],
        radius=10, fill=GOLD, outline=GOLD_LIGHT, width=2,
    )
    draw.rectangle([w / 2 - cap_w / 2, by0 - 70 - cap_h + 18, w / 2 + cap_w / 2, by0 - 70 - cap_h + 24], fill=GOLD_LIGHT)

    # subtle shadow under bottle
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([w / 2 - 150, by1 - 10, w / 2 + 150, by1 + 40], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=92)
    return buf.getvalue()


def make_scene_image(size, bg_tone, caption):
    """A simple atmospheric backdrop used for hero / about-us imagery."""
    w, h = size
    img = Image.new("RGB", size, bg_tone)
    draw = ImageDraw.Draw(img)
    random.seed(hash(caption) % 1000)
    for _ in range(40):
        x, y = random.uniform(0, w), random.uniform(0, h)
        r = random.uniform(1, 3)
        draw.ellipse([x, y, x + r, y + r], fill=(212, 175, 55, 120))
    png = make_bottle_image(bg_tone, (18, 46, 32), size=(size[0], size[1]), label=caption)
    return png


class Command(BaseCommand):
    help = "Seed demo perfume products with generated placeholder images"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing products first")

    def handle(self, *args, **options):
        if options["flush"]:
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING("Barcha mahsulotlar o'chirildi."))

        if Product.objects.exists():
            self.stdout.write(self.style.WARNING("Mahsulotlar allaqachon mavjud — o'tkazib yuborildi. --flush bilan qayta yarating."))
            return

        demo = [
            dict(name_uz="Zumrad Oud", name_ru="Изумрудный Уд", gender="unisex", concentration="parfum",
                 price=180, old_price=None, glass=(12, 58, 40), is_new=True, rating=4.9, reviews=124,
                 comp_uz="Oud, Safran, Amber, Sadr yog'ochi, Vanil",
                 desc_uz="Zumrad Oud — sharq va g'arb an'analarini uyg'unlashtirgan chuqur, boy hid. Kechki tadbirlar uchun ideal."),
            dict(name_uz="Yashil Aks-sado", name_ru="Эклат де Вер", gender="women", concentration="edp",
                 price=135, old_price=160, glass=(20, 80, 55), is_new=False, rating=4.8, reviews=98,
                 comp_uz="Bergamot, Yosemin, Muskus, Oq gul",
                 desc_uz="Yengil va nafis, bahorgi ertalablar uchun mos keladigan gulli-sitrus hid."),
            dict(name_uz="Qora Mutlaqlik", name_ru="Нуар Абсолю", gender="men", concentration="edp",
                 price=145, old_price=None, glass=(15, 15, 18), is_new=False, rating=4.9, reviews=156,
                 comp_uz="Qora murch, Charm, Vetiver, Tamaki",
                 desc_uz="Kuchli va sirli, tungi chiqishlar uchun yaratilgan erkaklar atiri."),
            dict(name_uz="Sadaf Oq", name_ru="Сантал Блан", gender="unisex", concentration="edt",
                 price=120, old_price=None, glass=(200, 195, 180), is_new=True, rating=4.7, reviews=87,
                 comp_uz="Sandal yog'ochi, Kokos, Musk, Vanil",
                 desc_uz="Yumshoq va iliq, kundalik foydalanish uchun qulay unisex hid."),
            dict(name_uz="Qirollik Atirgul", name_ru="Роз Империаль", gender="women", concentration="parfum",
                 price=160, old_price=190, glass=(90, 30, 45), is_new=False, rating=4.6, reviews=76,
                 comp_uz="Damashqi atirgul, Litchi, Pion, Oq muskus",
                 desc_uz="Nafis va qirollik ruhidagi atirgul hidi — nafosat ramzi."),
            dict(name_uz="Amber Kechasi", name_ru="Ночь Амбры", gender="men", concentration="parfum",
                 price=175, old_price=None, glass=(70, 45, 15), is_new=True, rating=4.8, reviews=64,
                 comp_uz="Amber, Tamaki bargi, Qora shokolad, Patchouli",
                 desc_uz="Iliq va shahvatli amber hidi, sovuq kechalar uchun mukammal."),
            dict(name_uz="Bahor Bog'i", name_ru="Весенний Сад", gender="women", concentration="edt",
                 price=98, old_price=None, glass=(30, 90, 60), is_new=False, rating=4.5, reviews=52,
                 comp_uz="Pion, Shaftoli, Oq muskus, Nilufar",
                 desc_uz="Yorqin va yengil gulli hid, kunduzgi kiyim uchun ajoyib tanlov."),
            dict(name_uz="Kumush Vetiver", name_ru="Серебряный Ветивер", gender="men", concentration="edt",
                 price=110, old_price=130, glass=(40, 55, 55), is_new=False, rating=4.6, reviews=71,
                 comp_uz="Vetiver, Grapefruit, Kashmir yog'ochi",
                 desc_uz="Yerga yaqin, tabiiy va zamonaviy erkaklar atiri."),
            dict(name_uz="Oltin Vanil", name_ru="Золотая Ваниль", gender="unisex", concentration="parfum",
                 price=155, old_price=None, glass=(95, 65, 20), is_new=True, rating=4.9, reviews=110,
                 comp_uz="Vanil, Tonka loviyasi, Karamel, Sadr",
                 desc_uz="Shirin va issiq, unutilmas taassurot qoldiruvchi gurmand hid."),
            dict(name_uz="Kristal Bahor", name_ru="Хрустальная Весна", gender="women", concentration="edp",
                 price=142, old_price=None, glass=(150, 190, 175), is_new=False, rating=4.7, reviews=68,
                 comp_uz="Nilufar, Bambuk, Oq muskus",
                 desc_uz="Toza va shaffof, suv sharsharasidek yengil hid."),
            dict(name_uz="Tungi Sadr", name_ru="Ночной Кедр", gender="men", concentration="edp",
                 price=132, old_price=None, glass=(25, 40, 30), is_new=False, rating=4.8, reviews=90,
                 comp_uz="Sadr yog'ochi, Qora murch, Vetiver, Amber",
                 desc_uz="Kuchli yog'ochsimon hid, ish va kechki tadbirlar uchun universal."),
            dict(name_uz="Shaffof Unisex", name_ru="Прозрачный Унисекс", gender="unisex", concentration="edc",
                 price=88, old_price=105, glass=(210, 210, 200), is_new=False, rating=4.4, reviews=40,
                 comp_uz="Bergamot, Oq choy, Muskus",
                 desc_uz="Yengil, sof va har kungi foydalanish uchun qulay atir."),
        ]

        created = 0
        for i, d in enumerate(demo):
            product = Product(
                name_uz=d["name_uz"],
                name_ru=d["name_ru"],
                brand="MYRON",
                gender=d["gender"],
                concentration=d["concentration"],
                volume_ml=random.choice([50, 75, 100]),
                price=d["price"],
                old_price=d.get("old_price"),
                short_description_uz=d["desc_uz"][:120],
                description_uz=d["desc_uz"],
                composition_uz=d["comp_uz"],
                rating=d["rating"],
                reviews_count=d["reviews"],
                is_new=d["is_new"],
                is_bestseller=d["reviews"] > 90,
                stock=random.choice([0, 15, 30, 60]),
            )
            png_bytes = make_bottle_image((13, 43, 31), d["glass"], label=d["concentration"])
            product.image.save(f"product_{i+1}.png", ContentFile(png_bytes), save=False)
            product.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} ta mahsulot yaratildi."))

        # Hero / about placeholder scene images
        import os
        img_dir = settings.BASE_DIR / "static" / "shop" / "img"
        img_dir.mkdir(parents=True, exist_ok=True)

        hero_png = make_bottle_image((10, 38, 27), (14, 58, 40), size=(900, 1100), label="Signature")
        with open(img_dir / "hero-placeholder.png", "wb") as f:
            f.write(hero_png)

        about1_png = make_bottle_image((8, 26, 18), (16, 48, 34), size=(900, 1000), label="Extrait")
        with open(img_dir / "about-1.png", "wb") as f:
            f.write(about1_png)

        about2_png = make_bottle_image((8, 26, 18), (60, 45, 20), size=(700, 700), label="Coffret")
        with open(img_dir / "about-2.png", "wb") as f:
            f.write(about2_png)

        self.stdout.write(self.style.SUCCESS("Hero/about placeholder rasmlari yaratildi."))
