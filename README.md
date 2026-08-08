# MYRON Perfume — Django saytі

Atir do'koni uchun to'liq funksional sayt: Django + SQLite, UZ/RU tillari,
savat (session asosida), buyurtma berish formasi, Telegram bot orqali
buyurtmalar haqida xabar, va zamonaviy admin panel.

## 1. O'rnatish

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_products     # 12 ta namunaviy mahsulot yaratadi (test uchun)
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/admin/

`seed_products` buyrug'i faqat demo/test uchun — u PIL yordamida generatsiya
qilingan atir shishasi rasmlari bilan 12 ta mahsulot yaratadi. Haqiqiy
mahsulotlaringizni admin panel orqali (rasm, nom, narx, tarkib va h.k.)
qo'shishingiz mumkin. Agar demo mahsulotlarni olib tashlab, qaytadan
yaratmoqchi bo'lsangiz: `python manage.py seed_products --flush`

## 2. Telegram bot sozlash (buyurtma xabarlari uchun)

1. Telegram'da **@BotFather** ga yozing → `/newbot` → botingiz nomini bering.
   Sizga bot **TOKEN** beriladi (masalan `123456:ABC-DEF...`).
2. O'zingizning **chat_id** raqamingizni bilish uchun **@userinfobot** ga
   yozing yoki botingizga bir marta `/start` yozib, so'ng brauzerda:
   `https://api.telegram.org/bot<TOKEN>/getUpdates` ni oching — u yerda
   `"chat":{"id": ...}` ko'rinadi.
3. Loyihaning tub papkasida `.env` fayl yarating (yoki muhit o'zgaruvchisi
   sifatida belgilang):

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export TELEGRAM_ADMIN_CHAT_ID="987654321"
```

Yoki `config/settings.py` faylida to'g'ridan-to'g'ri:

```python
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF..."
TELEGRAM_ADMIN_CHAT_ID = "987654321"
```

Shundan so'ng, saytda mijoz "Buyurtma berish" tugmasini bosib formani
to'ldirib tasdiqlaganda, botingizga mahsulot nomi, rasmi, narxi va mijoz
ma'lumotlari (ism, telefon, telegram username, izoh) bilan xabar keladi.

**Eslatma:** token sozlanmagan bo'lsa ham sayt ishlayveradi — buyurtma
bazaga (admin panelda ko'rinadi) saqlanadi, faqat Telegram xabari
yuborilmaydi (server logida ogohlantirish chiqadi).

## 3. Tarjimalar (UZ / RU)

Sayt matnlari `{% trans %}` teglar orqali ikki tilga tarjima qilingan.
Tarjimalar `locale/uz/` va `locale/ru/` papkalarida tayyor holda mavjud
(`.po` va kompilyatsiya qilingan `.mo` fayllar). Agar shablonlarga yangi
matn qo'shsangiz:

```bash
python manage.py makemessages -l uz -l ru
# locale/ru/LC_MESSAGES/django.po faylida yangi msgstr larni yozing
python manage.py compilemessages
```

Mahsulot nomi/tavsifi/tarkibi kabi ma'lumotlar esa admin panelda ikkala
til uchun alohida maydonlarga (`_uz` / `_ru`) kiritiladi.

## 4. Ishlab chiqarish (production) uchun eslatmalar

- `config/settings.py` da `DEBUG = False` qiling va `DJANGO_ALLOWED_HOSTS`
  muhit o'zgaruvchisiga domeningizni yozing.
- `DJANGO_SECRET_KEY` ni albatta almashtiring (muhit o'zgaruvchisi orqali).
- Statik fayllarni yig'ish: `python manage.py collectstatic`
- Ishlab chiqarishda SQLite o'rniga PostgreSQL/MySQL ishlatishni tavsiya
  qilamiz (yuqori yuklama bo'lsa), lekin kichik-o'rta do'kon uchun SQLite
  yetarli.
- Gunicorn + Nginx orqali serve qilish tavsiya etiladi.

## 5. Loyiha tuzilishi

```
config/          — Django sozlamalari, asosiy urls.py
shop/            — mahsulotlar, katalog, savat
orders/          — buyurtmalar, Telegram bot integratsiyasi
templates/       — barcha HTML shablonlar
static/shop/     — CSS, JS, placeholder rasmlar
locale/          — UZ/RU tarjimalar
media/products/  — yuklangan mahsulot rasmlari (admin orqali qo'shiladi)
```

## 6. Asosiy funksiyalar

- Sticky header (scroll qilganda yumshoq animatsiya bilan qisqaradi)
- Scroll-reveal animatsiyalar (mahsulotlar, bo'limlar sekin paydo bo'ladi)
- Katalog: jins (erkak/ayol/unisex), narx oralig'i, konsentratsiya bo'yicha
  filtr + saralash, cheksiz scroll (infinite scroll) bilan yuklash
- Mahsulot sahifasi: rasm galereyasi, miqdor tanlash, "Tavsif"/"Tarkibi"
  tablari, o'xshash mahsulotlar
- Savat: header'dagi ikonka orqali yon panel (drawer) ochiladi, miqdorni
  o'zgartirish, o'chirish — barchasi sahifa qayta yuklanmasdan (AJAX)
- Buyurtma berish: forma (ism, telefon, ixtiyoriy telegram va izoh) →
  tasdiqlash dialogi → muvaffaqiyat xabari → Telegram botga avtomatik xabar
- UZ / RU tilini almashtirish (header'dagi til tugmasi)
- To'liq responsive (mobil, planshet, desktop)
- Zamonaviy, brendga mos admin panel
