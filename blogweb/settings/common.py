import os, django_heroku


back = os.path.dirname

# 回溯父文件夹路径至根目录
BASE_DIR = back(back(back(os.path.abspath(__file__))))

### 分页设置 ###
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 4, # 当前页前后显示的页数
    'MARGIN_PAGES_DISPLAYED': 1,# 分页条前后显示页数
    'SHOW_FIRST_PAGE_WHEN_INVALID': True, # 当请求的页码不存在显示第一页
}

### 注册应用 ###
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    #'django.contrib.sitemaps',

    # 应用迁移不能删除migrations文件夹
    'blog.apps.BlogConfig',# 博客
    'comment.apps.CommentConfig',# 评论
    'account.apps.AccountConfig',# 账户
    'oauth.apps.OauthConfig',# 用户认证

    'pure_pagination',# 分页
    'compressor',# 静态文件加速器
    'mdeditor',# markdown编辑器
    'rest_framework',
    # 'haystack'# 搜索框架
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

### URL设置 ###
ROOT_URLCONF = 'blogweb.urls'

### 模板有关设置 ###
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blogweb.wsgi.application'


### 数据有关设置 ###
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        #'ENGINE': 'django.db.backends.mysql',
        #'NAME': 'blogweb_mysql',
        #'USER': 'root',
        #'PASSWORD': 'Ahxc1020@zhangxin.',
        #'HOST': 'localhost',
        # 'HOST': 'db',# 容器名
        #'PORT': '3306',
    }
}

#import dj_database_url
#DATABASES['default'] = dj_database_url.config()
#DATABASES['default'] = "postgres://cxqqxdkavxwkdw:8ab4b2d8809a2f2f252a12360242089fa88822ff758a3da5c96495344a7979b9@ec2-3-231-16-122.compute-1.amazonaws.com:5432/dfv2rlsh9im0ra"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


### 跨国应用设置 ###

# 简汉
LANGUAGE_CODE = 'zh-hans'

# 时区
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 是否使用UTC国际协调时间存储数据，为True可能造成模板与mysql数据库时间不一致问题
USE_TZ = False

### 静态文件设置 ####
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

# for all
STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
)

### 用户模型设置 ###
AUTH_USER_MODEL = 'account.BlogUser'
LOGIN_URL = '/login/'

### 日期格式设置 ###
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_TIME_FORMAT = '%Y-%m-%d'

### compress静态文件压缩配置 ###
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

### sites应用配置 ###
SITE_ID = 7

### 确认邮件发送配置 ###
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False# 安全传输协议
EMAIL_USE_SSL = True# 安全嵌套协议
EMAIL_HOST = 'smtp.qq.com'# 邮箱服务地址
EMAIL_PORT = 465# 端口号
EMAIL_HOST_USER = 'ahxc1020@qq.com'
EMAIL_HOST_PASSWORD = '***授权码***'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

django_heroku.settings(locals())
