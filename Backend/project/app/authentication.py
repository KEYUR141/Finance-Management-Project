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
        logger.debug("Password hashing operation initiated")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        logger.debug("Password hashing completed successfully")
        return hashed

    @staticmethod
    def authenticate(email_or_username, password):
        """Authenticate using UserProfile table only."""
        try:
            if "@" in email_or_username:
                user = UserProfile.objects.get(email__iexact=email_or_username)
                logger.debug(f"User lookup successful by email: {email_or_username}")
            else:
                user = UserProfile.objects.get(user_name__iexact=email_or_username)
                logger.debug(f"User lookup successful by username: {email_or_username}")
          
        except UserProfile.DoesNotExist:
            logger.warning(f"Authentication failed: User not found - {email_or_username}")
            raise AuthenticationFailed("Invalid credentials")

        hashed = UserAuthService.hash_password(password)
        if user.password_hash != hashed:
            logger.warning(f"Authentication failed: Invalid password for user {email_or_username}")
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            logger.warning(f"Authentication failed: Inactive user attempted login - {email_or_username}")
            raise AuthenticationFailed("User is inactive")

        logger.info(f"Authentication successful for user: {email_or_username} (UUID: {user.uuid})")
        return user

    @staticmethod
    def generate_tokens(user_profile):
        """
        SimpleJWT cannot create tokens for custom models.
        So we sync/create a Django User and issue JWT for that user.
        """
        logger.debug(f"Starting token generation for user: {user_profile.user_name}")
        
        django_user, created = User.objects.get_or_create(
            username=user_profile.user_name,
            defaults={"email": user_profile.email, "is_active": True}
        )
        
        if created:
            logger.info(f"New Django User created during token generation: {user_profile.user_name}")
        else:
            logger.debug(f"Existing Django User found: {user_profile.user_name}")

        if not user_profile.user:
                user_profile.user = django_user
                user_profile.save()
                logger.info(f"UserProfile linked to Django User: {user_profile.user_name}")

        refresh = RefreshToken.for_user(django_user)
        logger.info(f"JWT tokens generated successfully for user: {user_profile.user_name}")
        logger.debug(f"Token expiry - Access: 24 hours, Refresh: 24 hours")

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

    @staticmethod
    def login(email, password):
        """Main login workflow."""
        logger.info(f"Login attempt initiated for: {email}")
        
        try:
            user_profile = UserAuthService.authenticate(email, password)
            logger.debug(f"User authentication passed: {email}")

            tokens = UserAuthService.generate_tokens(user_profile)
            logger.info(f"Login completed successfully - User: {user_profile.user_name}, Email: {email}, Role: {user_profile.role}")

            return {
                "uuid": str(user_profile.uuid),
                "user_name": user_profile.user_name,
                "email": user_profile.email,
                "role": user_profile.role,
                "tokens": tokens
            }
        except AuthenticationFailed as e:
            logger.warning(f"Login failed for {email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login for {email}: {str(e)}", exc_info=True)
            raise
