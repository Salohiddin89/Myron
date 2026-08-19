"""
Django settings for MYRON Perfume project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-l$*xn-=ssgvhzg0$e2(wb(e8@#%)xocs&h!tuh=nb_zx8$0fa*",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000,http://192.168.1.52:8000",
).split(",")
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "shop.apps.ShopConfig",
    "orders.apps.OrdersConfig",
    "dashboard.apps.DashboardConfig",
]

MIDDLEWARE = [
    "config.security_middleware.CybersecurityMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------------------
# Cybersecurity & Hardening Settings
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Production SSL settings
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL", "False") == "True"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "shop.context_processors.cart_context",
                "shop.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "uz"

LANGUAGES = [
    ("uz", "O'zbekcha"),
    ("ru", "Русский"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True


# Static & media files
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(
    os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media"))
).expanduser()
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# MYRON custom settings
# ---------------------------------------------------------------------------

# Telegram bot notifications for new orders.
# Create a bot via @BotFather, get its token, and get your chat_id via @userinfobot
# (or the bot's getUpdates endpoint). Fill these in before going to production.
TELEGRAM_BOT_TOKEN = "8218372259:AAFXKY2LjAwHxEID4bhYZJMXcMA7peg9ehw"
TELEGRAM_ADMIN_CHAT_ID = "6296302270"

SITE_NAME = "MYRON"
SITE_PHONE = "+998 90 123 45 67"
SITE_EMAIL = "info@MYRON.uz"
SITE_ADDRESS_UZ = "Toshkent shahri, Amir Temur ko'chasi, 107B"
SITE_ADDRESS_RU = "г. Ташкент, проспект Амира Темура, 107B"
SITE_INSTAGRAM = "https://instagram.com/MYRON.perfume"
SITE_TELEGRAM = "https://t.me/MYRON_perfume"

CART_SESSION_ID = "cart"
