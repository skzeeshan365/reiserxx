from django.http import Http404, HttpResponse
from django.shortcuts import render

from main import utils


# Create your views here.


def home(request):
    items = [1, 2]
    return render(request, 'secondary/Test/home.html', {'items': items})


def first_home(request):
    return render(request, 'secondary/Test/birthday.html')


def first_no(request):
    return render(request, 'secondary/Test/No.html')


def first_no_2(request):
    return render(request, 'secondary/Test/No_2.html')


def first_yes(request):
    return render(request, 'secondary/Test/YES.html')


def first_yes_1(request):
    return render(request, 'secondary/Test/YES_2.html')


def second_home(request):
    return render(request, 'secondary/Test/index.html')


def second_mail(request):
    if request.method == 'POST':
        subject = "A New Message Is Received"

        message = "Hurrray, She said yes."

        to_email = 'skzeeshan3650@gmail.com'

        try:
            utils.send_email(subject=subject, message=message, to_email=to_email)
            return HttpResponse("Email sent successfully!")
        except Exception as e:
            pass
    else:
        raise Http404