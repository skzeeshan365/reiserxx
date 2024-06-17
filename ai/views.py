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
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        img = request.FILES.get('image')
        text = request.POST.get('text')

        if not img or not text:
            return JsonResponse({'error': 'File and text data are required'}, status=400)

        try:
            img = Image.open(img)
            # Optionally, you can resize or preprocess the image here if required
        except Exception as e:
            return JsonResponse({'error': 'Failed to process image: ' + str(e)}, status=400)

        # genai.configure(api_key=settings.GEMINI_API)
        # model = genai.GenerativeModel('gemini-1.5-flash')
        # response = model.generate_content([
        #     "describe this image.",
        #     img], stream=True)
        # response.resolve()

        response = json.dumps({"text": "Successful"})

        # Return JSON response with generated content
        return JsonResponse(response)

        # Handle other HTTP methods (GET, PUT, DELETE, etc.) if needed
    return JsonResponse({'error': 'Method not allowed'}, status=405)