from django import template

register = template.Library()

@register.simple_tag
def has_liked(article, user):
    """ユーザーがその投稿にいいねしているかどうかを確認する"""
    return article.like_set.filter(user=user).exists()