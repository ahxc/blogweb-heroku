# orm对象关系映射操作数据库
# 工具：批量生成测试数据
import os, pathlib, random, sys, django, faker

from datetime import timedelta
from django.utils import timezone

# 获取文件路径
back = os.path.dirname

# 获取根目录路径
# file为当前脚本完整路径
# back获取文件的父路径获取两次为根目录
BASE_DIR = back(back(os.path.abspath(__file__)))

# 添加根目录到python系统模块
sys.path.append(BASE_DIR)

### 环境和模型加载 ###
if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogweb.settings.local")
    django.setup()

    from blog.models import Category, Post, Tag
    from comment.models import Comment
    from account.models import BlogUser

### 每运行一次先清空数据库 ###
    print('clean database')
    Post.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Comment.objects.all().delete()
    BlogUser.objects.all().delete()

### 创造blog的基本属性 ###
    print('create a blog user')
    # 创建超级用户，账号，邮箱，密码
    user = BlogUser.objects.create_superuser('admin', 'admin@hellogithub.com', 'admin')

    category_list = ['类别1', '类别2', '类别3','类别4', '类别5']
    tag_list = ['标签1','标签2','标签3','标签4','标签5','标签6','标签7','标签8','标签9']
    a_year_ago = timezone.now() - timedelta(days=365)

    print('create categories and tags')
    for cate in category_list:
        Category.objects.create(name=cate)

    for tag in tag_list:
        Tag.objects.create(name=tag)

    print('create a markdown sample post')
    Post.objects.create(
        title='Markdown代码高亮测试',
        body=pathlib.Path(BASE_DIR).joinpath('scripts', 'md.sample').read_text(encoding='utf-8'),
        category=Category.objects.create(name='Markdown测试'),
        author=user,
        )

### 创建100篇英文post ###
    print('create some faked posts publised within the past year')
    # 建立faker对象，Faker 默认生成英文数据
    fake = faker.Faker()
    for _ in range(100):
        # 随机排序
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        # 返回指定区间的随机日期（-1y一年前）
        created_time = fake.date_time_between(start_date='-1y', end_date="now",
            # 根据 django 设置文件中TIME_ZONE的值返回对应的时区对象
            tzinfo=timezone.get_current_timezone())

        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            # 用于生成10个段落文本
            body='\n\n'.join(fake.paragraphs(10)),
            created_time=created_time,
            category=cate,
            author=user,
            )
        post.tags.add(tag1, tag2)
        post.save()



    print('done!')

### 创建100篇中文post ###
"""    print('create some comments')
    for post in Post.objects.all()[:20]:
        post_created_time = post.created_time
        delta_in_days = '-'+str((timezone.now()-post_created_time).days)+'d'
        for _ in range(random.randrange(3, 15)):
            Comment.objects.create(
                body=fake.paragraph(),
                created_time=fake.date_time_between(
                    start_date=delta_in_days,
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()),
                post=post,
                )"""