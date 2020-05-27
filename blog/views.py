
from django import forms
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify# 中文文本相关处理
from markdown.extensions.toc import TocExtension, slugify# 文本美化拓展
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.contrib import messages
from django.db.models import Q# 查询函数

from .models import Post, Category, Tag
from comment.forms import CommentForm


class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"#listview自动获取的文章列表
    # 只需指定属性：每paginate_by post一页
    paginate_by = 8


class CategoryView(IndexView):#继承
    def get_queryset(self):

        cate = get_object_or_404(Category, pk=self.kwargs.get("pk"))

        return super().get_queryset().filter(category=cate)


class ArchiveView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        # __为django语法
        # Mysql需要进行额外的时区设置
        return super().get_queryset().filter(created_time__year=year , created_time__month=month)


class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get("pk"))
        return super().get_queryset().filter(tags=tag)


class PostDetailView(DetailView):
    template_name = "blog/detail.html"

    model = Post

    pk_url_kwarg = "post_id"
    
    context_object_name = "post"

    def get_object(self, queryset=None):
        obj = super().get_object()
        obj.increase_views()
        self.object = obj

        return obj

    def get_context_data(self, **kwargs):
        postid = int(self.kwargs[self.pk_url_kwarg])
        comment_form = CommentForm()
        user = self.request.user

        # 如果用户已经登录，则隐藏邮件和用户名输入框
        if user.is_authenticated and not user.is_anonymous and user.email and user.username:
            comment_form.fields.update({
                "email": forms.CharField(widget=forms.HiddenInput()),
                "name": forms.CharField(widget=forms.HiddenInput()),})

            comment_form.fields["email"].initial = user.email
            comment_form.fields["name"].initial = user.username

        # 统计评论数
        post_comments = self.object.comment_list()
        kwargs["form"] = comment_form
        kwargs["post_comments"] = post_comments
        kwargs["comment_count"] = len(post_comments) if post_comments else 0

        kwargs["next_post"] = self.object.next_post
        kwargs["prev_post"] = self.object.prev_post

        return super().get_context_data(**kwargs)


### 搜索 ###
def search(request):
    # 获得前端输入参数keywords
    keywords = request.GET.get("keywords")
 
    if not keywords:
        error_msg = "请输入搜索关键词"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags="danger")
 
    post_list = Post.objects.filter(Q(title__icontains=keywords) | Q(body__icontains=keywords))

    return render(request, "blog/index.html", {"post_list": post_list})