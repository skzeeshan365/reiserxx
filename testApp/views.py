from django.shortcuts import render, redirect
from django.contrib.auth.models import auth


def wish(request):
    return render(request, "birthday.html")
