from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.urls import reverse

class BlogUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=50, blank=True)

    created_time = models.DateTimeField('创建时间', default=now)

    last_modify_time = models.DateTimeField('修改时间', default=now)

    source = models.CharField('创建来源', max_length=100, blank=True)

    # 返回绝对路径函数
    def get_absolute_url(self):
        return reverse(
            'blog:author_detail', kwargs={'author_name': self.username})

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['id']
        verbose_name = "账户"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'