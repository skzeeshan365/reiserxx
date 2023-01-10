import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        return HttpResponse(data.get('image'))
