from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

from ars.models import User


class WxAuthAuthenticationBackEnd(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, response=None, **kwargs):
        if response is None:
            return None
        if ('openid' not in response) or (response['openid'] is None):
            return None
        try:
            user = User.objects.get(openid=response['openid'])
        except User.DoesNotExist:
            return None
        return user


class WebAuthAuthenticationBackEnd(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, response=None, **kwargs):
        if request is None:
            return None
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user is not None and self.user_can_authenticate(
                user) and user.is_active and user.is_staff and check_password(password,
                                                                              user.password):
            return user
