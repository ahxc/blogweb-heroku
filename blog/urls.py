from django.urls import path

from . import views


# 将视图函数关联至blog应用防止视图函数命名重名
app_name = "blog"# 前端url命名空间，应用名称

urlpatterns = [
    # path url函数只接收函数，as_view将class转换为函数
    path('', views.IndexView.as_view(), name="index"),
    path('categories/<int:id>/', views.CategoryView.as_view(), name="category"),
    path('tags/<int:id>/', views.TagView.as_view(), name="tag"),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name="detail"),
    path('archive/<int:year>/<int:month>/', views.ArchiveView.as_view(), name="archive"),
    path('search/', views.search, name="search"),
]