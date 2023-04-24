from datetime import datetime
from django.shortcuts import render

def predict(request):
    if request.method == 'POST':

    else:
        return render(request, 'form.html')
