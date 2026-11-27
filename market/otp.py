from django.utils import timezone
from rest_framework.permissions import BasePermission


OTP_VALIDITY_SECONDS = 60 * 60


def get_otp_expiration(request):
    confirmation = request.session.get("otp")
    if not confirmation or confirmation["user_id"] != request.user.pk:
        return None

    expires_at = confirmation["expires_at"]
    if expires_at > timezone.now().timestamp():
        return expires_at
    return None


class OTPRequired(BasePermission):
    message = F"Подтвердите двухфакторную аутентификацию в профиле. Подтверждение действует {OTP_VALIDITY_SECONDS} минут."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_otp_expiration(request) is not None