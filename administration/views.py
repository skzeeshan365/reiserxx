from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from .models import Logs, Images
from reiserx.Resources import CONSTANTS


def login_page(request):
    logs = Logs.objects.all().order_by('-id')
    return render(request, "login.html", {'logs': logs, 'const': CONSTANTS})


def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('logs')
        else: return render(request, "login.html")
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return redirect('logs')


def logview(request, pk):
    logs = Logs.objects.get(id=pk)
    list = logs.images.all()
    return render(request, "test.html", {'logs': logs, 'img': list})

