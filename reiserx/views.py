from django.shortcuts import render
import pyrebase


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
