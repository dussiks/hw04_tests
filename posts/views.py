from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    """Return 10 posts per page beginning from last."""
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {"page": page, "paginator": paginator}
    return render(request, "index.html", context)

def group_posts(request, slug):
    """Return 10 posts per page in group beginning from last."""
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.all().order_by('-pub_date')
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
    username = get_object_or_404(User, username=username)
    user_post_list = username.posts.all().order_by('-pub_date')
    paginator = Paginator(user_post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_quantity = username.posts.count()
    context = {
        "page": page,
        "username": username,
        "paginator": paginator,
        "posts_quantity": posts_quantity,
        }
    return render(request, 'profile.html', context)

def post_view(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = username.posts.get(id=post_id)
    posts_quantity = username.posts.count()
    context = {
        "post": post,
        "posts_quantity": posts_quantity,
        "username": username,
        }
    return render(request, 'post.html', context)

def post_edit(request, username, post_id):
    username = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=username, id=post_id)
    if request.user != username:
        return redirect(reverse('post', args=[username, post_id]))
    form = PostForm(data=request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse('post', args=[username, post_id]))
    context = {
        "form": form,
        "is_edit": True,
        "post": post}
    return render(request, 'posts/new.html', context)
