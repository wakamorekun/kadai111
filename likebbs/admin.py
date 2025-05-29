# likebbs/admin.py

from django.contrib import admin
from .models import Article, Like, Post, PostLike

# 既存のモデル
admin.site.register(Article)
admin.site.register(Like)

# 新しいモデルの管理画面設定
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'author', 'created_at', 'like_count']
    list_filter = ['genre', 'created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def like_count(self, obj):
        return obj.like_count()
    like_count.short_description = 'いいね数'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']