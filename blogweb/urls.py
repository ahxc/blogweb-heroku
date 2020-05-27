
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from blog.feeds import AllPostsRssFeed

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('', include('account.urls')),
    path('', include('comment.urls')),
    path('', include('oauth.urls')),
    path('all/rss/', AllPostsRssFeed(), name='rss'),
    path("api/", include(router.urls)),# 自动注册视图函数
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
]