from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic    # 汎用ビューのインポート
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse    # reverse_lazy関数をインポート
from .models import Article, Like     # models.pyのArticleクラスとLikeクラスをインポート


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