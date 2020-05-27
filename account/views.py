import logging

from django.contrib import auth
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, RedirectView
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import RegisterForm, LoginForm
from scripts.tools import get_md5, send_email, get_current_site


logger = logging.getLogger(__name__)


class RegisterView(FormView):
    form_class = RegisterForm

    template_name = 'account/registration_form.html'

    # 表单有效性验证
    def form_valid(self, form):
        # 表单有效则保存用户但不提交到数据库
        if form.is_valid():
            user = form.save(False)
            user.is_active = False# 设置未激活
            user.source = 'Register'
            user.save(True)# 提交到数据库

            # 获得域名
            site = get_current_site().domain
            sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))

            # 如果开启了DEBUG本地调试模式则改为本地域名访问
            if settings.DEBUG:
                site = '127.0.0.1:8000'

            # 反解析视图函数获取URL中的路径
            path = reverse('account:result')

            url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(
                site=site, path=path, id=user.id, sign=sign)

            content = """
            <p>请点击下面链接验证您的邮箱</p>
            <a href="{url}" rel="bookmark">{url}</a>
            <br />
            """.format(url=url)

            title = '验证邮件'

            send_email(
                emailto=[
                    user.email,# 来自继承属性
                ],
                title=title,
                content=content)

            # 跳转到result通知页面
            url = reverse('account:result') + \
                '?type=register&id=' + str(user.id)

            return HttpResponseRedirect(url)

        # 表单无效
        else:
            return self.render_to_response({
                'form': form
            })


def account_result(request):
    # 获取此次操作类型，验证类型在注册邮件url中获得
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)

    # 如果用户激活成功跳转首页
    if user.is_active:
        return HttpResponseRedirect('/')

    if type in ['register', 'validation']:
        if type == 'register':
            content = '''
            恭喜您注册成功，一封验证邮件已经发送到您的邮箱：{email}，请登录您的邮箱完成本次验证。
            '''.format(email=user.email)

            title = '验证邮件'

        else:
            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')

            if sign != c_sign:
                return HttpResponseForbidden()

            # 激活
            user.is_active = True
            user.save()

            content = '''
            恭喜您已经完成邮箱验证，您现在可以使用您的账号来登录本站。
            '''

            title = '验证成功'

        return render(request, 'account/result.html', {
            'title': title,
            'content': content
        })

    # 如果是已激活账户返回首页
    else:
        return HttpResponseRedirect('/')


class LoginView(FormView):
    # 登录表单
    form_class = LoginForm

    # FormView该属性为小写
    # 用以保存转向成功的网址
    redirect_field_name = REDIRECT_FIELD_NAME

    template_name = 'account/login.html'

    # 成功认证后要跳转的URL名称
    success_url = '/'

    # csrf，利用已有的认证信息建立虚假请求进行操作
    @method_decorator(sensitive_post_parameters('password'))# 敏感信息保护，括号内为要保护的字段
    @method_decorator(csrf_protect)# 跨站请求攻击保护Cross Site Request Forgery
    @method_decorator(never_cache)# 禁用缓存
    def dispatch(self, request, *args, **kwargs):
        # dispatch将请求转给相应的方法，如无则引发HttpResponseNotAllowed
        # 这么做有利于套用多种修饰方法
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name)

        if redirect_to is None:
            redirect_to = '/'# 重定向loginview

        kwargs['redirect_to'] = redirect_to

        # get_context_data可以用于给模板传递模型以外的内容或参数
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # 认证
        # 用于验证的表单类
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            from scripts.tools import cache
            if cache is not None:
                cache.clear()

            logger.info(self.redirect_field_name)

            # 登录
            # 接受一个HttpRequest对象以及一个已认证的User对象
            auth.login(self.request, form.get_user())

            # 调用父类FormView的方法form_valid跳转到成功页面
            return super().form_valid(form)

        # 无效认证表单，重新渲染页面
        else:
            return self.render_to_response({
                'form':form})


class LogoutView(RedirectView):
    # 要重定向的URL
    url = '/login/'

    # @method_decorator与修饰符@不同的是，为函数添加self属性以适配类视图函数，其余相同
    @method_decorator(never_cache)
    def dispathch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from scripts.tools import cache
        cache.clear()

        # 注销
        logout(request)

        # 父类重定向到url
        return super().get(request, *args, **kwargs)