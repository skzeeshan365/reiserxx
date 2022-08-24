from django.shortcuts import render, redirect
import pyrebase

from .Resources import CONSTANTS
from .models import Media
from .models import Message
from .models import DriverDownloadUrl
from dotenv import load_dotenv
import os
from django.contrib import messages

from .models import ChangeLog

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

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def home(request):
    medias = Media.objects.all()
    message = Message.objects.all()
    downloadUrl = DriverDownloadUrl.objects.get(pk=1).url
    return render(request, "index.html", {'medias': medias, 'const': CONSTANTS, 'message': message, "REISERX_DRIVER_DOWNLOAD_URL": downloadUrl})


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
        data = {"fullname": val1, "email": val2, "message": val3}

        if db.child("Administration").child("Web").child("contact").push(data):
            messages.info(request, 'success: 1')  # submission response
        else:
            messages.info(request, 'fail: 0')  # submission response

        return redirect('home')
    else:
        return redirect('home')


def media(request, pk):
    medias = Media.objects.get(id=pk)
    return render(request, "message.html", {'medias': medias})


def changelogs(request):
    logs = ChangeLog.objects.all().order_by('-id')
    return render(request, "changeLogs.html", {'logs': logs, 'const': CONSTANTS})
