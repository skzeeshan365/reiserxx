from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth

from main.forms import PostForm
from main.models import Post
from .models import Logs
from reiserx.models import Contact
from reiserx.Resources import CONSTANTS
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


def login_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        logs = Logs.objects.all().order_by('-id')
        return render(request, "secondary/login.html", {'logs': logs, 'const': CONSTANTS})
    else:
        return render(request, "secondary/login.html", {'const': CONSTANTS})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('logs')
        else:
            messages.info(request, 'invalid credentials')
            return render(request, "secondary/login.html")
    else:
        return render(request, "secondary/login.html")


def logout(request):
    auth.logout(request)
    return redirect('logs')


@login_required
def logview(request, pk):
    logs = Logs.objects.get(id=pk)
    list = logs.images.all()
    return render(request, "secondary/test.html", {'logs': logs, 'img': list, 'const': CONSTANTS})

@login_required
def delete(request, pk):
    logs = Logs.objects.get(id=pk)
    logs.delete()
    return redirect('logs')


@login_required
def contacts(request):
    if request.user.is_authenticated and request.user.is_superuser:
        contacts_model = Contact.objects.all().order_by('-id')
        return render(request, "secondary/contact_messages.html", {'contacts': contacts_model})
    else:
        return render(request, "secondary/login.html", {'const': CONSTANTS})


@user_passes_test(lambda u: u.is_superuser)
def post_create_view(request):
    PostFormSet = modelformset_factory(Post, form=PostForm, extra=1)
    if request.method == 'POST':
        formset = PostFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect('post_new')
    else:
        formset = PostFormSet(queryset=Post.objects.none())
    return render(request, 'main/update.html', {'formset': formset})