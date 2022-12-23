import os
import time

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from dotenv import load_dotenv

from .Resources import CONSTANTS
from .models import ChangeLog
from .models import DriverDownloadUrl
from .models import Media
from .models import Message

load_dotenv('.env')

apiKey = os.getenv('apiKey')
authDomain = os.getenv('authDomain')
databaseURL = os.getenv('databaseURL')
projectId = os.getenv('projectId')
storageBucket = os.getenv('storageBucket')
messagingSenderId = os.getenv('messagingSenderId')
appId = os.getenv('appId')
measurementId = os.getenv('measurementId')

config = {
    "apiKey": apiKey,
    "authDomain": authDomain,
    "databaseURL": databaseURL,
    "projectId": projectId,
    "storageBucket": storageBucket,
    "messagingSenderId": messagingSenderId,
    "appId": appId,
    "measurementId": measurementId
}


def home(request):
    # medias = Media.objects.all()
    # message = Message.objects.all()
    return render(request, "index.html", {'const': CONSTANTS})


def policy(request):
    return render(request, "policy.html", {'const': CONSTANTS})


def reiserxpolicy(request):
    return render(request, "reiserxpolicy.html", {'const': CONSTANTS})


def terms(request):
    return render(request, "termsofuse.html", {'const': CONSTANTS})


def setupguide(request):
    return render(request, "setup.html", {'const': CONSTANTS})


def contact(request):
    if request.method == 'POST':

        # Submit contact form
        val1 = request.POST['fullname']
        val2 = request.POST['email']
        val3 = request.POST['message']

        substring = 'Cryto'
        substring2 = 'Baing'

        milliseconds = int(round(time.time() * 1000))
        data = {"fullname": val1, "email": val2, "message": val3, "timestamp": milliseconds}

        # medias = Media.objects.all()
        # message = Message.objects.all()
        # downloadUrl = DriverDownloadUrl.objects.get(pk=1).url
        return render(request, "index.html", {'const': CONSTANTS, 'issubmitted': True})
    else:
        return redirect('home')


def media(request, pk):
    # medias = Media.objects.get(id=pk)
    return render(request, "message.html")


def changelogs(request):
    # logs = ChangeLog.objects.all().order_by('-id')
    return render(request, "changeLogs.html", {'const': CONSTANTS})


def portfolio(request):
    return render(request, "portfolio.html")
