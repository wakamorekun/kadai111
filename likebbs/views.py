# likebbs/views.py (更新版)
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib import messages
from .models import Post, Like
from .forms import PostSearchForm

class IndexView(generic.ListView):
    """投稿一覧画面（検索機能付き）"""
    model = Post
    template_name = 'likebbs/index.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author').annotate(
            like_count=Count('like')
        )
        
        # 検索フォームからのパラメータを取得
        form = PostSearchForm(self.request.GET)
        
        if form.is_valid():
            # キーワード検索
            keyword = form.cleaned_data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) |
                    Q(content__icontains=keyword) |
                    Q(author__username__icontains=keyword)
                )
            
            # ジャンル絞り込み
            genre = form.cleaned_data.get('genre')
            if genre:
                queryset = queryset.filter(genre=genre)
            
            # 並び順
            ordering = form.cleaned_data.get('ordering')
            if ordering == 'oldest':
                queryset = queryset.order_by('created_at')
            elif ordering == 'popular':
                queryset = queryset.order_by('-like_count', '-created_at')
            else:  # newest (default)
                queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PostSearchForm(self.request.GET)
        context['genres'] = Post.GENRE_CHOICES
        
        # 統計情報
        context['stats'] = {
            'total_posts': Post.objects.count(),
            'total_users': Post.objects.values('author').distinct().count(),
            'total_likes': Like.objects.count(),
        }
        
        return context

class DetailView(generic.DetailView):
    """投稿詳細画面"""
    model = Post
    template_name = 'likebbs/detail.html'
    context_object_name = 'post'
    
    def get_object(self):
        obj = super().get_object()
        # いいね数を注釈として追加
        return Post.objects.annotate(
            like_count=Count('like')
        ).get(pk=obj.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_liked'] = Like.objects.filter(
                post=self.object,
                user=self.request.user
            ).exists()
        else:
            context['user_liked'] = False
        
        # 関連投稿（同じジャンルの最新投稿）
        context['related_posts'] = Post.objects.filter(
            genre=self.object.genre
        ).exclude(pk=self.object.pk).order_by('-created_at')[:5]
        
        return context

class CreateView(LoginRequiredMixin, generic.CreateView):
    """新規投稿画面"""
    model = Post
    template_name = 'likebbs/create.html'
    fields = ['title', 'genre', 'content']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, '投稿を作成しました。')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Bootstrapクラスを追加
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form

class UpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """投稿編集画面"""
    model = Post
    template_name = 'likebbs/create.html'
    fields = ['title', 'genre', 'content']
    
    def test_func(self):
        """投稿者のみ編集可能"""
        post = self.get_object()
        return self.request.user == post.author
    
    def form_valid(self, form):
        messages.success(self.request, '投稿を更新しました。')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Bootstrapクラスを追加
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form

class DeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """投稿削除画面"""
    model = Post
    template_name = 'likebbs/delete.html'
    success_url = reverse_lazy('likebbs:index')
    
    def test_func(self):
        """投稿者のみ削除可能"""
        post = self.get_object()
        return self.request.user == post.author
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '投稿を削除しました。')
        return super().delete(request, *args, **kwargs)

@login_required
def like_post(request, pk):
    """いいね機能のAjaxビュー"""
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            # 既にいいねしている場合は削除
            like.delete()
            liked = False
        else:
            liked = True
        
        # いいね数を取得
        like_count = Like.objects.filter(post=post).count()
        
        return JsonResponse({
            'liked': liked,
            'count': like_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# likebbs/forms.py (新規作成)
from django import forms
from .models import Post

class PostSearchForm(forms.Form):
    """投稿検索フォーム"""
    keyword = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'キーワードを入力...',
        }),
        label='キーワード'
    )
    
    genre = forms.ChoiceField(
        choices=[('', 'すべて')] + Post.GENRE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='ジャンル'
    )
    
    ORDERING_CHOICES = [
        ('newest', '新しい順'),
        ('oldest', '古い順'),
        ('popular', '人気順'),
    ]
    
    ordering = forms.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        initial='newest',
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='並び順'
    )

# likebbs/models.py (いいね機能を追加)
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
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_genre_display()}"
    
    def get_absolute_url(self):
        return reverse("likebbs:detail", kwargs={"pk": self.pk})

class Like(models.Model):
    """いいねモデル"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
        verbose_name = 'いいね'
        verbose_name_plural = 'いいね一覧'
    
    def __str__(self):
        return f"{self.user.username} -> {self.post.title}"