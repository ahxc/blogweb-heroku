from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import widgets
from captcha.fields import CaptchaField

from .models import BlogUser


class RegisterForm(UserCreationForm):
    """
    注册表单
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "账户", "class": "form-control"})

        self.fields['email'].widget = widgets.EmailInput(
            attrs={'placeholder': "邮箱", "class": "form-control"})

        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={'placeholder': "密码", "class": "form-control"})

        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={'placeholder': "再次确认密码", "class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data['email']

        # get_user_model()返回当前活动的用户模型
        # 如果指定了自定义用户模型，则返回自定义用户模型，否则返回User
        if get_user_model().objects.filter(email=email).exists():
            # raise抛出异常
            raise ValidationError("该邮箱已经存在")

        return email

    class Meta():
        model = get_user_model()
        fields = ("username", "email")

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        # 继承并补充__init__
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "账户", "class": "form-control"})

        self.fields['password'].widget = widgets.PasswordInput(
            attrs={'placeholder': "密码", "class": "form-control"})

        self.fields['captcha'].widget = CaptchaField(label='验证码')

