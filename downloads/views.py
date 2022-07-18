
from django.shortcuts import render
from django.shortcuts import HttpResponse
import pyrebase

from dotenv import load_dotenv
import os

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


def downloadfiles(request):
    val2 = request.GET['email']
    val1 = request.GET['fullname']

    if val1 != 'null' and val2 != 'null':
        data = {"fullname": val1, "email": val2}
        db.child("Administration").child("Web").child("downloads").push(data)


        return render(request, 'download.html')

def download(request):
    return render(request, "download.html")