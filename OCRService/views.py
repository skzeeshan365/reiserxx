import json
import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from google.cloud import vision
from google.oauth2 import service_account


@csrf_exempt
def process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        response = process_request(data.get('image'))
    return HttpResponse(response)


def process_request(data):
    load_dotenv('.env')

    type = os.getenv('vision_type')
    project_id = os.getenv('vision_project_id')
    private_key_id = os.getenv('vision_private_key_id')
    private_key = os.getenv('vision_private_key')
    client_email = os.getenv('vision_client_email')
    client_id = os.getenv('vision_client_id')
    auth_uri = os.getenv('vision_auth_uri')
    token_uri = os.getenv('vision_token_uri')
    auth_provider_x509_cert_url = os.getenv('vision_auth_provider_x509_cert_url')
    client_x509_cert_url = os.getenv('vision_client_x509_cert_url')

    CREDENTIALS = {
        "type": type,
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": auth_uri,
        "token_uri": token_uri,
        "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
        "client_x509_cert_url": client_x509_cert_url
    }
    # calling up google vision json file
    credentials = service_account.Credentials.from_service_account_info(CREDENTIALS)

    client = vision.ImageAnnotatorClient(credentials=credentials)

    content = data

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image, image_context={"language_hints": ["en-t-i0-handwrit"]})

    if response.error.message:
        return response.error.message
    else:
        return response.full_text_annotation.text