from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    """Return 10 posts per page beginning from last."""
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {"page": page, "paginator": paginator}
    return render(request, "index.html", context)


def group_posts(request, slug):
    """Return 10 posts per page in group beginning from last."""
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.all()
    paginator = Paginator(group_post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
        "paginator": paginator,
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('/')
    context = {'form': form, 'is_edit': False}
    return render(request, 'posts/new.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts_list = author.posts.all()
    paginator = Paginator(author_posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_count = author.posts.count()
    context = {
        "page": page,
        "author": author,
        "paginator": paginator,
        "posts_count": posts_count,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    posts_count = author.posts.count()
    context = {
        "post": post,
        "posts_count": posts_count,
        "author": author,
    }
    return render(request, 'post.html', context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(data=request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    context = {
        "form": form,
        "is_edit": True,
        "post": post,
    }
    return render(request, 'posts/new.html', context)
