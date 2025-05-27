from django.contrib import admin
from .models import Article, Like # models.pyからArticleとLikeクラスをインポート

admin.site.register(Article)    # DjangoAdminにArticleクラスを登録
admin.site.register(Like)       # DjangoAdminにLikeクラスを登録