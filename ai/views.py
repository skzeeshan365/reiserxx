import json
import os

from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
from django.views.decorators.csrf import csrf_exempt

from djangoProject1 import settings


# Create your views here.

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def home(request):
    return HttpResponse("API based only")


@csrf_exempt
def multimodel(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if auth_header != os.getenv('PYTHON_KEY'):
            return HttpResponse('Unauthorized', status=401)

        img = request.FILES.get('image')
        text = request.POST.get('text')

        if not img or not text:
            return HttpResponse('File and text data are required', status=400)

        try:
            img = Image.open(img)
        except Exception as e:
            return HttpResponse('Failed to process image: ' + str(e), status=400)

        try:
            genai.configure(api_key=settings.GEMINI_API)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([
                text,
                img], stream=True)
            response.resolve()
            response = response.text
            return JsonResponse({"response": response})
        except Exception as e:
            return HttpResponse('Failed to generate response, please try again later', status=500)

        # Handle other HTTP methods (GET, PUT, DELETE, etc.) if needed
    return HttpResponse('Method not allowed', status=405)