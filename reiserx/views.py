from django.shortcuts import render
import pyrebase
from django.http import HttpResponse
from django.utils.encoding import smart_str


def home(request):
    return render(request, "index.html")


def policy(request):
    return render(request, "policy.html")


def terms(request):
    return render(request, "termsofuse.html")


def contact(request):
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

    val1 = request.POST['fullname']
    val2 = request.POST['email']
    val3 = request.POST['message']

    data = {"fullname": val1, "email": val2, "message": val3}
    db.child("Administration").child("Web").child("contact").push(data)

    return render(request, "index.html")


def downloadReiserX(request):
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
    storage = firebase.storage()

    response = HttpResponse(
        content_type='application/download')  # mimetype is replaced by content_type for django 1.7
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str("ReiserX.apk")
    response['X-Sendfile'] = smart_str(storage.child("App/Target/app-release.apk"))
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response