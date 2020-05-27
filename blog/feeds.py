from django.contrib.syndication.views import Feed
from .models import Post

### RSS控件 ###
class AllPostsRssFeed(Feed):
    # XML标题
    title = "blogweb"

    # 跳转的网站地址
    link = "/"

    # 描述信息
    description = "全部文章"

    # 需要显示的内容
    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return "[%s] %s" % (item.category, item.title)

    def item_description(self, item):
        return item.body_html