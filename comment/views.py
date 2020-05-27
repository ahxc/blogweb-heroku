
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.generic.edit import FormView

from .forms import CommentForm
from .models import Comment
from blog.models import Post


class CommentPostView(FormView):
    form_class = CommentForm

    template_name = "blog/detail.html"

    def get(self, request, *args, **kwargs):
        post_id = self.kwargs["post_id"]

        post = Post.objects.get(pk=post_id)

        url = post.get_absolute_url()

        return HttpResponseRedirect(url+"#comments")

    def form_invalid(self, form):
        post_id = self.kwargs["post_id"]

        post = Post.objects.get(pk=post_id)

        if self.request.user.is_authenticated:
            form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })

            user = self.request.user

            form.fields["email"].initial = user.email

            form.fields["name"].initial = user.username

        return self.render_to_response({
            "form": form,
            "post": post})

    def form_valid(self, form):
        user = self.request.user

        post_id = self.kwargs["post_id"]

        post = Post.objects.get(pk=post_id)

        if not self.request.user.is_authenticated:

            email = form.cleaned_data['email']
            
            username = form.cleaned_data['name']

            user = get_user_model().objects.get_or_create(
                username=username, email=email)[0]

        # 保存但不写入数据库
        comment = form.save(False)

        # 和评论列表关联起来
        comment.post = post

        comment.author = user

        if form.cleaned_data['parent_comment_id']:
            parent_comment = Comment.objects.get(
                pk=form.cleaned_data['parent_comment_id'])

            comment.parent_comment = parent_comment

        comment.save(True)

        # 输出次级url+评论id
        return HttpResponseRedirect(
            "%s#div-comment-%d" %
            (post.get_absolute_url(), comment.pk))