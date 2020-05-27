from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


### 用户名或邮箱登录设置 ###
class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 用户名和邮箱登录的支持
        if '@' in username:
            kwargs = {'email': username}

        else:
            kwargs = {'username': username}

        try:
            user = get_user_model().objects.get(**kwargs)

            if user.check_password(password):
                return user

        except get_user_model().DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)

        except get_user_model().DoesNotExist:
            return None