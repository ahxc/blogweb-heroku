from django.conf.urls import url
from django.urls import path
from . import views
from .forms import LoginForm


app_name = "account"


urlpatterns = [
    # r 正则表达式 ^匹配字符串开头，$匹配字符串末尾
    url(r'^login/$',
        views.LoginView.as_view(success_url='/'),
        name='login',
        kwargs={'authentication_form':LoginForm}),

    url(r'^register/$',
        views.RegisterView.as_view(),
        name='register'),

    url(r'^logout/$',
        views.LoginView.as_view(),
        name='logout'),

    path(r'account/result.html',
        views.account_result,
        name='result'),
]