from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from app.models import UserProfile
from django.contrib.auth.models import User
import hashlib
import logging

logger = logging.getLogger(__name__)


class UserAuthService:

    @staticmethod
    def hash_password(password: str):
        """Hash password with SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate(email_or_username, password):
        """Authenticate using UserProfile table only."""
        try:
            if "@" in email_or_username:
                user = UserProfile.objects.get(email__iexact=email_or_username)
            else:
                user = UserProfile.objects.get(user_name__iexact=email_or_username)
          
        except UserProfile.DoesNotExist:
            logger.warning(f"Login failed: Email not found → {email_or_username}")
            raise AuthenticationFailed("Invalid credentials")

        hashed = UserAuthService.hash_password(password)
        if user.password_hash != hashed:
            logger.error(f"Wrong password for {email_or_username}")
            logger.warning(f"Received hashed: '{hashed}' | Stored: '{user.password_hash}'")
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        return user

    @staticmethod
    def generate_tokens(user_profile):
        """
        SimpleJWT cannot create tokens for custom models.
        So we sync/create a Django User and issue JWT for that user.
        """
        django_user, created = User.objects.get_or_create(
            username=user_profile.user_name,
            defaults={"email": user_profile.email, "is_active": True}
        )

        if not user_profile.user:
                user_profile.user = django_user
                user_profile.save()

        refresh = RefreshToken.for_user(django_user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

    @staticmethod
    def login(email, password):
        """Main login workflow."""
        user_profile = UserAuthService.authenticate(email, password)

        tokens = UserAuthService.generate_tokens(user_profile)

        return {
            "uuid": str(user_profile.uuid),
            "user_name": user_profile.user_name,
            "email": user_profile.email,
            "role": user_profile.role,
            "tokens": tokens
        }
