
from django import forms
from django.forms import ModelForm

from .models import Comment

class CommentForm(forms.ModelForm):
    url = forms.URLField(label="网址", required=False)

    email = forms.EmailField(label="邮箱", required=True)

    name = forms.CharField(
        label="姓名",
        widget=forms.TextInput(
            attrs={
                'placeholder': "写下你的评论..",
                'value': '',
                'size': '30',
                'maxlength': '245',
                'aria-required': 'true'
            }))

    # 隐藏部件评论框
    parent_comment_id = forms.IntegerField(
        widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment

        fields = ['body'] 