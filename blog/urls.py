from django.urls import path
from .views import index

from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'),
    path('category/<int:pk>', views.CategoryView.as_view(), name='category'),
    path('tags/<int:pk>', views.TagView.as_view(), name='tag'),
    path('search/', views.search, name='search'),
    #path('api/index/', views.IndexPostListAPIView.as_view()),
    path("api/index/", index),
]