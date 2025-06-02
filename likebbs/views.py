from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Post

class IndexView(generic.ListView):
    """投稿一覧画面"""
    model = Post
    template_name = 'likebbs/index.html'
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

class DetailView(generic.DetailView):
    """投稿詳細画面"""
    model = Post
    template_name = 'likebbs/detail.html'
    context_object_name = 'post'

class CreateView(LoginRequiredMixin, generic.CreateView):
    """新規投稿画面"""
    model = Post
    template_name = 'likebbs/create.html'
    fields = ['title', 'genre', 'content']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class UpdateView(LoginRequiredMixin, generic.UpdateView):
    """投稿編集画面"""
    model = Post
    template_name = 'likebbs/create.html'
    fields = ['title', 'genre', 'content']
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class DeleteView(LoginRequiredMixin, generic.DeleteView):
    """投稿削除画面"""
    model = Post
    template_name = 'likebbs/delete.html'
    success_url = reverse_lazy('likebbs:index')
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)