from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

def send_password_reset_email(user):
    token = default_token_generator.make_token(user)
    uid = user.pk
    reset_url = reset_url = f"{settings.BACKEND_URL}/api/accounts/password-reset-form/?uid={uid}&token={token}"

    subject = "Set or Reset Your Password"
    message = f"""
    Hello {user.email},

    Someone requested to set or reset your password.
    Click below:

    {reset_url}

    Ignore this if unexpected.
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
