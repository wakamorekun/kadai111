from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from .models import Article, Like, Post, PostLike



# IndexViewクラスを作成
class IndexView(generic.ListView):
    model = Article     # Articleモデルを使用 
    template_name = 'likebbs/index.html'    # 使用するテンプレート名を指定（Articleも自動で渡す）
    ordering = ['-created_at']  # 新しい投稿順に並べる
    
# DetailViewクラスを作成
class DetailView(generic.DetailView):
    model = Article
    template_name = 'likebbs/detail.html'
    
# CreateViewクラスを作成
class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Article
    template_name = 'likebbs/create.html'
    fields = ['content']  # 内容のみ入力可能に変更
    
    # フォーム送信時の処理をオーバーライド
    def form_valid(self, form):
        # 現在のユーザーを投稿者として設定
        form.instance.author = self.request.user
        return super().form_valid(form)
    
# UpdateViewクラスを作成
class UpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Article
    template_name = 'likebbs/create.html'
    fields = ['content']  # 内容のみ編集可能に変更
    
# DeleteViewクラスを作成
class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Article
    template_name = 'likebbs/delete.html'
    success_url = reverse_lazy('likebbs:index')

# いいね処理用のビュー
class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        like, created = Like.objects.get_or_create(article=article, user=request.user)
        
        # 既にいいねしていた場合は削除する（トグル機能）
        if not created:
            like.delete()
            
        # リダイレクト先の指定（一覧ページへ）
        return redirect('likebbs:index')

# Ajaxでいいね処理を行うためのAPIビュー
class LikeAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        like, created = Like.objects.get_or_create(article=article, user=request.user)
        
        # 既にいいねしていた場合は削除する（トグル機能）
        is_liked = created
        if not created:
            like.delete()
            is_liked = False
            
        # いいねの数を返す
        like_count = article.like_count()
        
        # JSON形式でレスポンスを返す
        return JsonResponse({'liked': is_liked, 'count': like_count})
# likebbs/views.py に追加するビュー（既存のビューはそのまま保持）


# 既存のArticle関連のビューはそのまま保持...

# 新しいPost関連のビュー
class PostIndexView(generic.ListView):
    model = Post
    template_name = 'likebbs/post_index.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.all()
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Post.GENRE_CHOICES
        context['selected_genre'] = self.request.GET.get('genre', '')
        return context

class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'likebbs/post_detail.html'
    context_object_name = 'post'

class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Post
    template_name = 'likebbs/post_create.html'
    fields = ['title', 'genre', 'content']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Post
    template_name = 'likebbs/post_create.html'
    fields = ['title', 'genre', 'content']
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Post
    template_name = 'likebbs/post_delete.html'
    success_url = reverse_lazy('likebbs:post_index')
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        
        if not created:
            like.delete()
            
        return redirect('likebbs:post_detail', pk=post.pk)

class PostLikeAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        
        is_liked = created
        if not created:
            like.delete()
            is_liked = False
            
        like_count = post.like_count()
        
        return JsonResponse({'liked': is_liked, 'count': like_count})