from django.db import models
from django.contrib.auth.models import User # Userモデルをインポート
from django.urls import reverse # reverse関数をインポート

class Article(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # その投稿の詳細ページへのリンク
    def get_absolute_url(self):
        return reverse("likebbs:detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.content
    
    def like_count(self):
        """いいねの数を返す"""
        return self.like_set.count()

class Like(models.Model):
    """いいねモデル"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # 同じ記事に同じユーザーが複数回いいねできないようにする
        unique_together = ('article', 'user')
    
    def __str__(self):
        return f"{self.user} likes {self.article}"