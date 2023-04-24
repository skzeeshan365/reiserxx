from datetime import datetime
from django.shortcuts import render


def predict(request):
    return render(request, 'form.html')
