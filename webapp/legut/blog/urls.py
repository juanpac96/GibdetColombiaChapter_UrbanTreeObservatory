from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),  # Página de inicio
    path('blog/', views.PostList.as_view(), name='blog'),  # Página del blog
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
]

#urlpatterns = [
#    path('', views.PostList.as_view(), name='home'),
#    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
#    path('blog/', views.blog, name='blog')
#]
