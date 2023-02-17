from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import auth


def wish(request):
    title = "Title"
    message = "Message"
    return render(request, 'birthday.html', {'title': title, 'message': message})
