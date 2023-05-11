import base64
import os

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import auth
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from djangoProject1 import settings
from main.models import Post, Category, Tag
from .forms import PostForm, CategoryForm, PostFormEdit


def login_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('post_new')
    else:
        return render(request, "secondary/login.html")


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('post_new')
        else:
            messages.info(request, 'invalid credentials')
            return render(request, "secondary/login.html")
    else:
        return render(request, "secondary/login.html")


def logout(request):
    auth.logout(request)
    return redirect('logs')


@user_passes_test(lambda u: u.is_superuser)
def post_create_view(request):
    PostFormSet = modelformset_factory(Post, form=PostForm, extra=1)
    if request.method == 'POST':
        formset = PostFormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.author = request.user  # set the author field to the currently logged-in user
                instance.save()
            formset.save()
            return redirect('post_new')
    else:
        formset = PostFormSet(queryset=Post.objects.none())
    return render(request, 'Administration/update.html', {'formset': formset, 'new': True})


def post_list(request):
    all_posts = Post.objects.all()
    return render(request, 'Administration/postlist.html', {'items': all_posts, 'list': True})


def post_edit(request, post_slug):
    instance = get_object_or_404(Post, slug=post_slug)
    form = PostFormEdit(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('post_list')
    return render(request, 'Administration/postlist.html', {'form': form, 'list': False})


def category(request):
    CategoryFormSet = modelformset_factory(Category, form=CategoryForm, extra=1)
    if request.method == 'POST':
        formset = CategoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect('category')
    else:
        formset = CategoryFormSet()
    return render(request, 'Administration/update_category.html', {'formset': formset})


def robots_txt(request):
    try:
        with open(os.path.join(settings.BASE_DIR, 'robots.txt'), 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = ["User-agent: *\n", "Disallow: /"]
    return HttpResponse(''.join(lines), content_type='text/plain')


def post_preview(request):
    post = Post()
    if request.method == 'POST':
        data = dict(request.POST)
        print(data)

        post.title = data['form-0-title'][0]
        post.content = data['form-0-content'][0]
        post.description = data['form-0-description'][0]
        post.category = Category.objects.get(pk=data['form-0-category'][0])
        post.pk = 999999999
        for tag_name in data['form-0-tags'][0].split(','):
            tag_name = tag_name.strip()
            tag, created = Tag.objects.get_or_create(tag=tag_name)
            post.tags.add(tag)
        image = request.FILES['form-0-image']
        post.image = 'data:image/png;base64,' + base64.b64encode(image.read()).decode('utf-8')
        post.author = request.user

    return render(request, 'Administration/post.html', {'post': post})