import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


def validate_image_file(file):
    """Validates uploaded image files:
    - Extension check (.jpg, .jpeg, .png, .webp, .gif, .svg)
    - Content-Type check (must start with image/)
    - Size check (<= 10MB)
    """
    if not file:
        return file

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _("Faqat ruxsat berilgan rasm formatlari yuklanishi mumkin (JPG, PNG, WEBP, GIF, SVG).")
        )

    if hasattr(file, "size") and file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            _("Rasm hajmi 10 MB dan oshmasligi kerak.")
        )

    if hasattr(file, "content_type") and file.content_type:
        if not file.content_type.startswith("image/"):
            raise ValidationError(
                _("Yuklangan fayl haqiqiy rasm fayli bo'lishi kerak.")
            )

    return file
