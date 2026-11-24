from django.core.cache import cache
from django.utils import timezone
from rest_framework.permissions import BasePermission


OTP_VALIDITY_SECONDS = 10 * 60


def otp_cache_key(user_id, session_key):
    return f"otp_good:{user_id}:{session_key}"


def get_session_otp_key(request):
    if not request.session.session_key:
        request.session.create()
    return otp_cache_key(request.user.pk, request.session.session_key)


class OTPRequired(BasePermission):
    message = "Подтвердите двухфакторную аутентификацию в профиле. Подтверждение действует 10 минут."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        expires_at = cache.get(get_session_otp_key(request), 0)
        return expires_at > timezone.now().timestamp()
