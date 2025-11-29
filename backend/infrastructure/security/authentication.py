from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.settings import api_settings
from infrastructure.persistence.models import Users
from django.utils.translation import gettext_lazy as _

class UserWrapper:
    """
    Wrapper for Users model to provide Django Auth compatibility
    without modifying the auto-generated model.
    """
    def __init__(self, user):
        self._user = user

    def __getattr__(self, name):
        return getattr(self._user, name)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True
        
    @property
    def pk(self):
        return self._user.id
        
    def __str__(self):
        return str(self._user.id)

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = Users.objects.using('neon').get(id=user_id)
        except Users.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        # Wrap the user to provide auth properties
        return UserWrapper(user)
