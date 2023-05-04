import os

import cloudinary
from cloudinary.uploader import upload
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth
from dotenv import load_dotenv

from djangoProject1 import settings
from .forms import PostForm, CategoryForm, PostFormEdit
from main.models import Post, Category
from django.contrib import messages


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


def tinymce_upload(request):
    load_dotenv('.env')

    CLOUD_NAME = os.getenv('CLOUD_NAME')
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')

    if request.method == 'POST':
        image = request.FILES.get('image')
        result = cloudinary.uploader.upload(image, api_key=API_KEY, api_secret=API_SECRET, cloud_name=CLOUD_NAME, folder='reiserx')
        return JsonResponse({'location': result['secure_url']})
    elif request.method == 'DELETE':
        filename = request.GET.get('filename')
        try:
            cloudinary.uploader.destroy(filename, api_key=API_KEY, api_secret=API_SECRET, cloud_name=CLOUD_NAME)
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponse(status=400)