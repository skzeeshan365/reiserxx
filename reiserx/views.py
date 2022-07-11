from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, "index.html")


def policy(request):
    return render(request, "policy.html")


def terms(request):
    return render(request, "termsofuse.html")
