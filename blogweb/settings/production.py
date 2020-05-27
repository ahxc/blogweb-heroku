from .common import *
#from django.core.management import utils

# 随机的密钥生成会破坏会话
#production_secret_key = utils.get_random_secret_key()
#SECRET_KEY = production_secret_key
SECRET_KEY = 'n9ceqv38)#&mwuat@(mjb_p%em$e8$qyr#fw9ot!=ba6lijx-6'

DEBUG = True

ALLOWED_HOSTS = ['blogweb-django.herokuapp.com']

# HAYSTACK_CONNECTIONS['default']['URL'] = 'http://hellodjango_blog_tutorial_elasticsearch:9200/'
