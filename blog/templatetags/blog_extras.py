from django import template
from django.db.models.aggregates import Count
from django.db.models import Q
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from random import sample

from blog.models import Category
from ..models import Post, Category, Tag


register = template.Library()


"""
修饰器，引用之前定义的一个函数，参数为修饰的函数（修饰器下方）
需要注意的：
函数先定义，再修饰它；反之会编译器不认识；
修饰符“@”后面必须是之前定义的某一个函数；
每个函数只能有一个修饰符组成修饰器，多个修饰器可修饰同一个函数；
多个修饰器由下往上逐步喂参
"""
### 侧边栏 ###

# 最近文章列表
@register.inclusion_tag('blog/inclusions/_recent_posts.html', takes_context=True)
def show_recent_posts(context, num=5):
    return {# 表示逆序由今至古
        'recent_post_list': Post.objects.all().order_by('-created_time')[:num],
    }


# 分类
@register.inclusion_tag('blog/inclusions/_categories.html', takes_context=True)
def show_categories(context):
    # 统计分类下的文章数，同时过滤文章数为0的分类及不显示
    category_list = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'category_list': category_list,
    }


# 标签云
@register.inclusion_tag('blog/inclusions/_tags.html', takes_context=True)
def show_tags(context):
    tag_list = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'tag_list': tag_list,
    }


# 归档
@register.inclusion_tag('blog/inclusions/_archives.html', takes_context=True)
def show_archives(context):
    return {
        # DESC降序
        'date_list': Post.objects.dates('created_time', 'month', order='DESC'),
    }


# 推荐阅读
@register.inclusion_tag('blog/inclusions/_recommended_reading.html', takes_context=True)
def show_recommended_reading(context, post, num=5):
    # 选出同类别，删除掉自身,取反不等于
    same_category_list = list(Post.objects.filter(Q(category=post.category) & ~Q(title=post.title)))
    if len(same_category_list) > 5:
        same_category_list = sample(same_category_list, 5)
    return {
        # 随机抽取5个
        'same_category_list': same_category_list,
    }


# 选取关键字有关的数据
# {% query post_comments parent_comment=None as parent_comments %}
@register.simple_tag
def query(qs, **kwargs):

    # return post_comments.filter(parent_comment=None as parent_comments)
    return qs.filter(**kwargs)


@register.filter(is_safe=True)
@stringfilter
def custom_markdown(content):
    from scripts.tools import CommonMarkdown

    return mark_safe(CommonMarkdown.get_markdown(content))