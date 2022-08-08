from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from .models import Logs


def login_page(request):
    logs = Logs.objects.all().order_by('-id')
    return render(request, "login.html", {'logs': logs})


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

