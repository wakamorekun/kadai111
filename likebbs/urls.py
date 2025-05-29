# likebbs/urls.py

from django.urls import path
from . import views

app_name = 'likebbs'

urlpatterns = [
    # 既存のArticle関連のURL
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.UpdateView.as_view(), name="update"),
    path('<int:pk>/delete/', views.DeleteView.as_view(), name="delete"),
    path('<int:pk>/like/', views.LikeView.as_view(), name="like"),
    path('api/<int:pk>/like/', views.LikeAPIView.as_view(), name="like_api"),
    
    # 新しいPost関連のURL
    path('posts/', views.PostIndexView.as_view(), name='post_index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/update/', views.PostUpdateView.as_view(), name="post_update"),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name="post_delete"),
    path('posts/<int:pk>/like/', views.PostLikeView.as_view(), name="post_like"),
    path('posts/api/<int:pk>/like/', views.PostLikeAPIView.as_view(), name="post_like_api"),
]