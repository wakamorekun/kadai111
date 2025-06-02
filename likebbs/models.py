from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    """投稿モデル"""
    GENRE_CHOICES = [
        ('tech', 'テクノロジー'),
        ('business', 'ビジネス'),
        ('lifestyle', 'ライフスタイル'),
        ('entertainment', 'エンターテイメント'),
        ('sports', 'スポーツ'),
        ('education', '教育'),
        ('travel', '旅行'),
        ('food', '食べ物'),
        ('health', '健康'),
        ('other', 'その他'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='タイトル')
    genre = models.CharField(
        max_length=20, 
        choices=GENRE_CHOICES, 
        default='other',
        verbose_name='ジャンル'
    )
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name='投稿者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日')
    
    class Meta:
        verbose_name = '投稿'
        verbose_name_plural = '投稿一覧'
        ordering = ['-created_at']  # 新しい投稿順に並べる
    
    def __str__(self):
        return f"{self.title} - {self.get_genre_display()}"
    
    def get_absolute_url(self):
        return reverse("likebbs:detail", kwargs={"pk": self.pk})