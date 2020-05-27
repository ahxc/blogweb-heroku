from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy
from django.urls import reverse

from .models import Post, Category, Tag


class PostListFilter(admin.SimpleListFilter):
    title = ugettext_lazy("作者")
    parameter_name = "author"

    def lookups(self, request, model_admin):
        authors = list(set(map(lambda x: x.author, Post.objects.all())))
        for author in authors:
            yield (author.id, ugettext_lazy(author.username))

    def queryset(self, request, queryset):
        id = self.value()
        if id:
            return queryset.filter(author__id__exact=id)
        else:
            return queryset


class PostForm(forms.ModelForm):
    # body = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Post
        fields = '__all__'


def makr_post_publish(modeladmin, request, queryset):
    queryset.update(status='p')


def draft_post(modeladmin, request, queryset):
    queryset.update(status='d')


def close_post_commentstatus(modeladmin, request, queryset):
    queryset.update(comment_status='c')


def open_post_commentstatus(modeladmin, request, queryset):
    queryset.update(comment_status='o')


makr_post_publish.short_description = "发布选中文章"
draft_post.short_description = "选中文章设置为草稿"
close_post_commentstatus.short_description = "关闭文章评论"
open_post_commentstatus.short_description = "打开文章评论"


class PostAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('body', 'title')
    form = PostForm
    list_display = (
        'id',
        'title',
        'author',
        'link_to_category',
        'created_time',
        'views',
        'status',
        'type',
        'post_order')
    list_display_links = ('id', 'title')
    list_filter = (PostListFilter, 'status', 'type', 'category', 'tags')
    filter_horizontal = ('tags',)
    exclude = ('created_time', 'last_mod_time')
    view_on_site = True

    actions = [
        makr_post_publish,
        draft_post,
        close_post_commentstatus,
        open_post_commentstatus]

    def link_to_category(self, obj):
        info = (obj.category._meta.app_label, obj.category._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))

        return format_html(u'<a href="%s">%s</a>' % (link, obj.category.name))

    link_to_category.short_description = '分类目录'

    def get_form(self, request, obj=None, **kwargs):
        form = super(PostAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].queryset = get_user_model(
        ).objects.filter(is_superuser=True)
        return form

    def save_model(self, request, obj, form, change):
        super(PostAdmin, self).save_model(request, obj, form, change)

    def get_view_on_site_url(self, obj=None):
        if obj:
            url = obj.get_full_url()

            return url
        else:
            from scripts.tools import get_current_site
            site = get_current_site().domain

            return site


class TagAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'created_time')


class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug', 'last_mod_time', 'created_time')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)