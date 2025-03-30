from django.shortcuts import render
from django.views import generic
from .models import Post

# Create your views here.

def index(request):
    return render(request, 'index.html')

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog.html' # Cambia 'index.html' por 'blog.html'

class PostDetail(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'

def blog(request):
    return render(request, 'blog.html')
