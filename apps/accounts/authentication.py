"""Custom authentication backend for email-based login."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate using email (username field) or username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate with email OR username."""
        try:
            # Try to find user by email (which is stored as username in our system)
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If not found by username/email, return None
            return None

        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        """Get user by ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
