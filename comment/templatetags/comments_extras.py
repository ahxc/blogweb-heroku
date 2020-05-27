from django import template
from ..forms import CommentForm


register = template.Library()


@register.simple_tag
def parse_commenttree(commentlist, comment):
    datas = []

    def parse(c):
        childs = commentlist.filter(parent_comment=c, is_enable=True)
        for child in childs:
            datas.append(child)
            parse(child)

    parse(comment)
    return datas


@register.inclusion_tag('comment/inclusions/comment_item.html')
def show_comment_item(comment, ischild):
    depth = 1 if ischild else 2

    return {
        "comment_item": comment,
        "depth":depth
    }