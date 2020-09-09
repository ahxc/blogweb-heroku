import logging, mistune

from hashlib import md5
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.dispatch import Signal, receiver
from mistune import escape, escape_link


logger = logging.getLogger(__name__)

send_email_signal = Signal(
    providing_args=['emailto', 'title', 'content'])


def get_md5(str):
    m = md5(str.encode('utf-8'))

    return m.hexdigest()


@receiver(send_email_signal)
def send_email_signal_handler(sender, **kwargs):
    emailto = kwargs['emailto']
    title = kwargs['title']
    content = kwargs['content']

    # 邮件发送
    msg = EmailMultiAlternatives(
        title,
        content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=emailto)

    msg.content_subtype = "html"

    try:
        result = msg.send()

    except Exception as e:
        logger.error(e)


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except BaseException:
                key = None

            if not key:
                unique_str = repr((func, args, kwargs))

                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)

            if value is not None:

                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value

            else:
                logger.info(
                    'cache_decorator set cache:%s key:%s' %
                    (func.__name__, key))
                value = func(*args, **kwargs)

                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)

                return value

        return news

    return wrapper


@cache_decorator()
def get_current_site():

    return Site.objects.get_current()


def send_email(emailto, title, content):
    send_email_signal.send(
        send_email.__class__,
        emailto=emailto,
        title=title,
        content=content)


### markdown渲染 ###
class BlogMarkDownRenderer(mistune.Renderer):
    def block_code(self, text, lang=None):
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)

    def autolink(self, link, is_email=False):
        text = link = escape(link)

        if is_email:
            link = 'mailto:%s' % link
        if not link:
            link = "#"
        site = get_current_site()
        nofollow = "" if link.find(site.domain) > 0 else "rel='nofollow'"
        return '<a href="%s" %s>%s</a>' % (link, nofollow, text)

    def link(self, link, title, text):
        link = escape_link(link)
        site = get_current_site()
        nofollow = "" if link.find(site.domain) > 0 else "rel='nofollow'"
        if not link:
            link = "#"
        if not title:
            return '<a href="%s" %s>%s</a>' % (link, nofollow, text)
        title = escape(title, quote=True)
        return '<a href="%s" title="%s" %s>%s</a>' % (
            link, title, nofollow, text)


class CommonMarkdown():
    @staticmethod
    def get_markdown(value):
        renderer = BlogMarkDownRenderer(inlinestyles=False)

        mdp = mistune.Markdown(escape=True, renderer=renderer)
        return mdp(value)