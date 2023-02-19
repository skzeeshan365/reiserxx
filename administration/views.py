from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from .models import Logs
from reiserx.models import Contact
from reiserx.Resources import CONSTANTS
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        logs = Logs.objects.all().order_by('-id')
        return render(request, "login.html", {'logs': logs, 'const': CONSTANTS})
    else:
        return render(request, "login.html", {'const': CONSTANTS})


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
            return render(request, "login.html")
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return redirect('logs')


@login_required
def logview(request, pk):
    logs = Logs.objects.get(id=pk)
    list = logs.images.all()
    return render(request, "test.html", {'logs': logs, 'img': list, 'const': CONSTANTS})

@login_required
def delete(request, pk):
    logs = Logs.objects.get(id=pk)
    logs.delete()
    return redirect('logs')


@login_required
def contacts(request):
    if request.user.is_authenticated and request.user.is_superuser:
        contacts_model = Contact.objects.all().order_by('-id')
        return render(request, "contact_messages.html", {'contacts': contacts_model})
    else:
        return render(request, "login.html", {'const': CONSTANTS})

