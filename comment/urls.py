from django.urls import path

from . import views


app_name = 'comment'


urlpatterns = [
    path('comment/<int:post_id>', views.CommentPostView.as_view(), name="comment"),
]