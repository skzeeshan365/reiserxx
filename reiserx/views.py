from django.shortcuts import render
import pyrebase

from .Resources import CONSTANTS
from .models import Media

config = {
        "apiKey": "AIzaSyBxfeEYK42Z9_5J9QzHXOX1yxHUgVR-i8U",
        "authDomain": "testtrace-941f7.firebaseapp.com",
        "databaseURL": "https://testtrace-941f7-default-rtdb.firebaseio.com",
        "projectId": "testtrace-941f7",
        "storageBucket": "testtrace-941f7.appspot.com",
        "messagingSenderId": "145231816902",
        "appId": "1:145231816902:web:df232c954486dd83254fc7",
        "measurementId": "G-FCM9GH77KN"
    }

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def home(request):
    medias = Media.objects.all()
    return render(request, "index.html", {'medias': medias, 'const': CONSTANTS})


def policy(request):
    return render(request, "policy.html", {'const': CONSTANTS})


def terms(request):
    return render(request, "termsofuse.html", {'const': CONSTANTS})


def setupguide(request):
    return render(request, "setup.html", {'const': CONSTANTS})


def download(request):
    return render(request, "download.html")


def contact(request):
    val1 = request.POST['fullname']
    val2 = request.POST['email']
    val3 = request.POST['message']

    data = {"fullname": val1, "email": val2, "message": val3}
    db.child("Administration").child("Web").child("contact").push(data)

    return render(request, "index.html")


def downloadfiles(request):
    val1 = request.POST['fullname']
    val2 = request.POST['email']

    data = {"fullname": val1, "email": val2}
    db.child("Administration").child("Web").child("downloads").push(data)

    return render(request, 'download.html')
