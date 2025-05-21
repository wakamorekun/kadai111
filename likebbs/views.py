from django.shortcuts import render
from django.views import generic    # 汎用ビューのインポート
from .models import Article     # models.pyのArticleクラスをインポート
from django.urls import reverse_lazy    # reverse_lazy関数をインポート


# IndexViewクラスを作成
class IndexView(generic.ListView):
    model = Article     # Articleモデルを使用 
    template_name = 'likebbs/index.html'    # 使用するテンプレート名を指定（Articleも自動で渡す）
    
# DetailViewクラスを作成
class DetailView(generic.DetailView):
    model = Article
    template_name = 'likebbs/detail.html'
    
# CreateViewクラスを作成
class CreateView(generic.CreateView):
    model = Article
    template_name = 'likebbs/create.html'
    fields = '__all__'
    
# UpdateViewクラスを作成
class UpdateView(generic.UpdateView):
    model = Article
    template_name = 'likebbs/create.html'
    fields = '__all__'
    
# DeleteViewクラスを作成
class DeleteView(generic.DeleteView):
    model = Article
    template_name = 'likebbs/delete.html'
    success_url = reverse_lazy('likebbs:index')
