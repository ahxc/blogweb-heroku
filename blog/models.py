import logging

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.core.cache import cache
from abc import abstractmethod
from mdeditor.fields import MDTextField

from scripts.tools import cache_decorator, get_current_site


logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)

    created_time = models.DateTimeField("创建时间", default=now)

    last_mod_time = models.DateTimeField("修改时间", default=now)

    def save(self, *args, **kwargs):
        is_update_views = isinstance(self, Post) \
        and 'update_fields' in kwargs \
        and kwargs['update_fields'] == ['views']

        if is_update_views:
            Post.objects.filter(pk=self.pk).update(views=self.views)

        else:
            if 'slug' in self.__dict__:
                # getattr()返回指定类指定属性的值，这里返回name
                slug = getattr(
                    self, 'title') if 'title' in self.__dict__ else getattr(
                    self, 'name')

                # 与getattr不同在于设置指定类指定属性的值
                setattr(self, 'slug', slugify(slug))

            super().save(*args, **kwargs)

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site,
                                            path=self.get_absolute_url())

        return url

    class Meta:
        # 基类，不创建任何数据表
        abstract = True

    # 抽象类方法，其基类无法实例化（赋值过程），子类如果不复写被修饰的方法，也无法实例化
    @abstractmethod
    def get_absolute_url(self):
        pass


class Category(models.Model):
    # django 要求模型必须继承 models.Model 类

    name = models.CharField("分类", max_length=30, unique=True)

    parent_category = models.ForeignKey(
        "self",
        verbose_name="父级分类",
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse(
            'blog:category_detail', kwargs={
                'category_name': self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        categorys = []

        # 递归
        def parse(category):
            categorys.append(category)
            # 如果分类属性不为空(有父级分类)，继续解析父级分类，获得分类list
            if category.parent_category:
                parse(category.parent_category)

        parse(self)

        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            # 原理同上，获得除父级以外的所有子分类
            if category not in categorys:
                categorys.append(category)

            childs = all_categorys.filter(parent_category=category)

            for child in childs:
                if category not in categorys:
                    categorys.append(child)

                parse(child)

        parse(self)

        return categorys

class Tag(models.Model):
    name = models.CharField('标签名', max_length=30, unique=True)

    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_post_count(self):

        # 统计该标签下的文章数
        return Post.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name

class Post(BaseModel):

    STATUS_CHOICES = (
        ('d', "草稿"),
        ('p', "发表"),)

    COMMENT_STATUS = (
        ('o', "打开"),
        ('c', "关闭"),)

    TYPE = (
        ('a', "文章"),
        ('p', "页面"),)

    title = models.CharField("标题", max_length=200, unique=True)
    body = MDTextField("正文")
    pub_time = models.DateTimeField(
        "发布时间", blank=False, null=False, default=now)

    status = models.CharField(
        "文章状态",
        max_length=1,
        choices=STATUS_CHOICES,
        default='p')

    comment_status = models.CharField(
        "评论状态",
        max_length=1,
        choices=COMMENT_STATUS,
        default='o')

    type = models.CharField('类型', max_length=1, choices=TYPE, default='a')
    views = models.PositiveIntegerField('浏览量', default=0)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        blank=False,
        null=False,
        on_delete=models.CASCADE)

    post_order = models.IntegerField(
        "排序,数字越大越靠前", blank=False, null=False, default=0)

    category = models.ForeignKey(
        "Category",
        verbose_name="分类",
        on_delete=models.CASCADE,
        blank=False,
        null=False)

    tags = models.ManyToManyField('Tag', verbose_name="标签集合", blank=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-post_order", "-pub_time"]
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={
            "post_id": self.id})

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def increase_views(self):
        self.views += 1
        # 标志为update_fields字段，post类，字段为views
        self.save(update_fields=["views"])

    def comment_list(self):
        cache_key = "post_comments_{id}".format(id=self.id)
        value = cache.get(cache_key)

        if value:
            logger.info("get post comments:{id}".format(id=self.id))

            return value
        else:
            comments = self.comment_set.filter(is_enable=True)
            cache.set(cache_key, comments, 60 * 100)
            logger.info("set post comments:{id}".format(id=self.id))

            return comments

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)

        return reverse("admin:%s_%s_change" % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_post(self):
        # 下一篇
        return Post.objects.filter(
            id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_post(self):
        # 前一篇
        return Post.objects.filter(
            id__lt=self.id, status='p').order_by('-id').first()