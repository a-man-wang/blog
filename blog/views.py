from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from .models import Post, Category, Tag
import markdown
import re
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
from markdown.extensions.toc import TocExtension
from pure_pagination.mixins import PaginationMixin


# Create your views here.


# def index(request):
#     post_list = Post.objects.all()
#     return render(request, 'blog/index.html', context={
#         "post_list": post_list
#     })


class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 10


# def detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     post.increase_views()
#     md = markdown.Markdown(extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         # 记得在顶部引入 TocExtension 和 slugify
#         TocExtension(slugify=slugify),
#     ])
#     post.body = md.convert(post.body)
#
#     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
#     post.toc = m.group(1) if m is not None else ''
#
#     return render(request, 'blog/detail.html', context={'post': post})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super().get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            # 记得在顶部引入 TocExtension 和 slugify
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)

        m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
        # post.toc = m.group(1) if m is not None else ''

        return post


# def archive(request, year, month):
#     post_list = Post.objects.filter(created_time__year=year,
#                                     created_time__month=month
#                                     )
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class ArchiveView(IndexView):
    def get_queryset(self):
        # year = get_object_or_404(Post, year=self.kwargs.get('year'))
        # month = get_object_or_404(Post, month=self.kwargs.get('month'))
        return super(ArchiveView, self).get_queryset().filter(
            created_time__year=self.kwargs.get('year'),
            created_time__month=self.kwargs.get('month')
        )


# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


# def tag(request, pk):
#     t = get_object_or_404(Tag, pk=pk)
#     post_list = Post.objects.filter(tag=t)
#     return render(request, 'blog/index.html', context={'post_list': post_list})


class TagView(IndexView):
    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tag=t)


def search(request):
    key = request.GET.get('search_key')
    if not key:
        error_msg = "请输入搜索关键字"
        messages.add_message(request, messages.ERROR, error_msg, extrg_tags='danger')
        return render('blog/index')

    post_list = Post.objects.filter(Q(title__icontains=key) | Q(body__icontains=key))
    return render(request, 'blog/index.html', {'post_list': post_list})


'''
rest_framework
'''
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework import mixins

from .serializers import PostListSerializer


# @api_view(http_method_names=["GET"])
# def index(request):
#     post_list = Post.objects.all().order_by('-created_time')
#     serializer = PostListSerializer(post_list, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


class IndexPostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]


class PostViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pagination_class = LimitOffsetPagination
    serializer_class = PostListSerializer
    queryset = Post.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]


index = PostViewSet.as_view({'get': 'list'})
