import re
import time
import urllib.parse
from collections import defaultdict
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.translation import gettext as _

# In-memory IP rate limiter: { ip: [timestamp1, timestamp2, ...] }
_REQUEST_HISTORY = defaultdict(list)
_POST_HISTORY = defaultdict(list)

# Limits
MAX_GET_PER_MINUTE = 120
MAX_POST_PER_MINUTE = 20

# Malicious patterns (Path traversal, SQLi probes, XSS in query parameters)
SUSPICIOUS_PATTERNS = re.compile(
    r"(\.\.\/|\.\.\\|<script|union\s+select|select\s+.*\s+from|insert\s+into|delete\s+from|drop\s+table|<iframe|javascript:)",
    re.IGNORECASE,
)


class CybersecurityMiddleware:
    """Production-grade Security Middleware for MYRON Perfume.
    - Rate limits IPs to prevent DoS / Brute-force attacks.
    - Filters malicious payload patterns (Path traversal, SQLi, XSS).
    - Sets security headers (XSS, Nosniff, Clickjacking prevention).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        now = time.time()

        # 1. Inspect Query String & Request Path for malicious payloads
        full_path = urllib.parse.unquote(request.get_full_path())
        if SUSPICIOUS_PATTERNS.search(full_path):
            return HttpResponseForbidden("403 Forbidden: Security Exception Detected.")

        # 2. Rate Limiting Logic
        # Clean up old timestamps (> 60s ago)
        _REQUEST_HISTORY[ip] = [t for t in _REQUEST_HISTORY[ip] if now - t < 60]
        _POST_HISTORY[ip] = [t for t in _POST_HISTORY[ip] if now - t < 60]

        if len(_REQUEST_HISTORY[ip]) >= MAX_GET_PER_MINUTE:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"error": _("Juda ko'p so'rov yuborildi. Birozdan so'ng qayta urining.")}, status=429)
            return HttpResponseForbidden("429 Too Many Requests: Rate limit exceeded.")

        _REQUEST_HISTORY[ip].append(now)

        if request.method == "POST":
            if len(_POST_HISTORY[ip]) >= MAX_POST_PER_MINUTE:
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"error": _("So'rovlar soni cheklandi. Biroz kuting.")}, status=429)
                return HttpResponseForbidden("429 Too Many Requests: POST Rate limit exceeded.")
            _POST_HISTORY[ip].append(now)

        # 3. Process Request
        response = self.get_response(request)

        # 4. Enforce Hardened Security Headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
        return ip
