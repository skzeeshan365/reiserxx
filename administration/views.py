from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth

from .forms import PostForm, CategoryForm
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
    return render(request, 'main/update.html', {'formset': formset, 'new': True})


def post_edit(request):
    PostFormSet = modelformset_factory(Post, form=PostForm, extra=0)
    if request.method == 'POST':
        formset = PostFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect('post_new')
    else:
        formset = PostFormSet(queryset=Post.objects.all())
    return render(request, 'main/update.html', {'formset': formset, 'new': False})


def category(request):
    CategoryFormSet = modelformset_factory(Category, form=CategoryForm, extra=1)
    if request.method == 'POST':
        formset = CategoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect('category')
    else:
        formset = CategoryFormSet()
    return render(request, 'main/update_category.html', {'formset': formset})
