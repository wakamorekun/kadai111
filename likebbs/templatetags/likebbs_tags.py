from django import template
from ..models import PostLike

register = template.Library()

@register.simple_tag
def has_liked(article, user):
    """ユーザーがその投稿（Article）にいいねしているかどうかを確認する"""
    if not user.is_authenticated:
        return False
    return article.like_set.filter(user=user).exists()

@register.simple_tag
def has_liked_post(post, user):
    """ユーザーがその投稿（Post）にいいねしているかどうかを確認する"""
    if not user.is_authenticated:
        return False
    return PostLike.objects.filter(post=post, user=user).exists()

@register.filter
def get_genre_display(value):
    """ジャンルの表示名を取得する"""
    from ..models import Post
    genre_dict = dict(Post.GENRE_CHOICES)
    return genre_dict.get(value, value)