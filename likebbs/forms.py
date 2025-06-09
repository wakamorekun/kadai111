# ========== likebbs/forms.py ==========
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post

class PostSearchForm(forms.Form):
    """投稿検索フォーム"""
    keyword = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'タイトル、内容、投稿者で検索...',
        }),
        label='キーワード検索'
    )
    
    genre = forms.ChoiceField(
        choices=[('', 'すべてのジャンル')] + Post.GENRE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='ジャンル'
    )
    
    ORDERING_CHOICES = [
        ('newest', '新しい順'),
        ('oldest', '古い順'),
        ('popular', '人気順（いいね数）'),
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

class CustomUserCreationForm(UserCreationForm):
    """カスタムユーザー登録フォーム"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrapクラスを追加
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # プレースホルダーを設定
        self.fields['username'].widget.attrs['placeholder'] = 'ユーザー名'
        self.fields['password1'].widget.attrs['placeholder'] = 'パスワード'
        self.fields['password2'].widget.attrs['placeholder'] = 'パスワード確認'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# ========== likebbs/templatetags/__init__.py ==========
# (空のファイル)

# ========== likebbs/templatetags/likebbs_tags.py ==========
from django import template
from django.contrib.auth.models import User
from ..models import Like

register = template.Library()

@register.simple_tag
def has_liked_post(post, user):
    """ユーザーが投稿にいいねしているかチェック"""
    if not user.is_authenticated:
        return False
    return Like.objects.filter(post=post, user=user).exists()

@register.filter
def multiply(value, arg):
    """数値の掛け算フィルター"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.inclusion_tag('likebbs/includes/post_card.html')
def render_post_card(post, user):
    """投稿カードをレンダリング"""
    return {
        'post': post,
        'user': user,
        'user_liked': Like.objects.filter(post=post, user=user).exists() if user.is_authenticated else False,
    }

# ========== accounts/forms.py ==========
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class CustomAuthenticationForm(AuthenticationForm):
    """カスタムログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrapクラスを追加
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['username'].widget.attrs['placeholder'] = 'ユーザー名'
        self.fields['password'].widget.attrs['placeholder'] = 'パスワード'

class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ========== accounts/views.py ==========
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

class CustomLoginView(LoginView):
    """カスタムログインビュー"""
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f'ようこそ、{form.get_user().username}さん！')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """カスタムログアウトビュー"""
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'ログアウトしました。')
        return super().dispatch(request, *args, **kwargs)

class RegisterView(CreateView):
    """ユーザー登録ビュー"""
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('likebbs:index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'アカウントを作成しました。ようこそ、{self.object.username}さん！')
        return response

@login_required
def profile_view(request):
    """プロフィール表示・編集"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロフィールを更新しました。')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'registration/profile.html', {
        'form': form,
        'user_posts_count': request.user.post_set.count(),
        'user_likes_count': request.user.like_set.count(),
    })

# ========== accounts/urls.py ==========
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
]

# ========== likebbs/models.py (更新版) ==========
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
    
    @property
    def like_count(self):
        """いいね数を取得"""
        return self.like_set.count()

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

# ========== likebbs/urls.py (更新版) ==========
from django.urls import path
from . import views

app_name = 'likebbs'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.UpdateView.as_view(), name="update"),
    path('<int:pk>/delete/', views.DeleteView.as_view(), name="delete"),
    path('<int:pk>/like/', views.like_post, name='like'),
    
    # 新しいURL（post_プレフィックス付き）
    path('posts/', views.PostIndexView.as_view(), name='post_index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/update/', views.PostUpdateView.as_view(), name="post_update"),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name="post_delete"),
    path('posts/<int:pk>/like/', views.post_like, name='post_like'),
    path('posts/api/<int:pk>/like/', views.api_like_post, name='api_like'),
]

# ========== settings.py の追加設定 ==========
# LOGIN_URL = '/accounts/login/'
# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/'

# INSTALLED_APPS に以下を追加:
# 'accounts',