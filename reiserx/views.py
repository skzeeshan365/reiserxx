from django.shortcuts import render, redirect
from django.templatetags.static import static

from .Resources import CONSTANTS
from .models import ChangeLog
from .models import Media
from .models import Message


def home(request):
    medias = Media.objects.all()
    message = Message.objects.all()
    download_url = "https://firebasestorage.googleapis.com/v0/b/testtrace-941f7.appspot.com/o/App%2FTarget%2Fapp-release.apk?alt=media&token=72e1ce18-e3b2-4701-9a94-c7a187e9cb4c"
    return render(request, "secondary/index.html", {'medias': medias, 'const': CONSTANTS, 'message': message,
                                          "REISERX_DRIVER_DOWNLOAD_URL": download_url})


def policy(request):
    return render(request, "secondary/policy.html", {'const': CONSTANTS})


def reiserxpolicy(request):
    return render(request, "secondary/reiserxpolicy.html", {'const': CONSTANTS})


def terms(request):
    return render(request, "secondary/termsofuse.html", {'const': CONSTANTS})


def setupguide(request):
    return render(request, "secondary/setup.html", {'const': CONSTANTS})


def contact(request):
    return redirect('contact')


def media(request, pk):
    medias = Media.objects.get(id=pk)
    return render(request, "secondary/message.html", {'medias': medias})


def changelogs(request):
    logs = ChangeLog.objects.all().order_by('-id')
    return render(request, "secondary/changeLogs.html", {'logs': logs, 'const': CONSTANTS})


def portfolio(request):
    return render(request, "secondary/portfolio.html", {'file': static('portfolio.pdf'), 'message': "Download my portfolio, currently it's in pdf form!"})


def farae_policy(request):
    return render(request, "secondary/Test/farae_policy.html")