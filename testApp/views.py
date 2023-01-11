from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import auth


def wish(request):
    str1 = '''a = 3\nb = 6\nres = a + b\nprint(res)'''
    return HttpResponse(exec(str1))
