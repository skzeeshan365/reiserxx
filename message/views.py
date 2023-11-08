from django.http import Http404
from django.shortcuts import render

# Create your views here.


def home(request):
    raise Http404


def no(request):
    return render(request, 'secondary/Test/No.html')


def no_2(request):
    return render(request, 'secondary/Test/No_2.html')

def yes(request):
    return render(request, 'secondary/Test/YES.html')


def yes_1(request):
    return render(request, 'secondary/Test/YES_2.html')