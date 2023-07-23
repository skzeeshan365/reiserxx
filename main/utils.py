import io
import json

import requests
import vocalhost
from PIL import Image

from djangoProject1 import settings


def handle_uploaded_image(f):
    # Open the uploaded image in RGBA format
    img = Image.open(f)
    # Convert the image to RGB format
    img = img.convert('RGB')
    # Save the image to a byte stream
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=75)
    output.seek(0)
    # Return the byte stream
    return output


def get_token():
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'username': settings.VERIFALIA_USERNAME,
        'password': settings.VERIFALIA_PASSWORD
    }

    response = requests.post('https://api.verifalia.com/v2.4/auth/tokens', headers=headers, json=data)
    if response.status_code == 200:
        token = response.json()['accessToken']
        return token, None
    else:
        return None, f'Error: {response.status_code}'


# Step 2: Validate an email address using the obtained token
def is_valid_email(email):
    token, err = get_token()

    api_endpoint = 'https://api.verifalia.com/v2.4/email-validations'

    payload = {
        'entries': [
            {
                'inputData': email,
            }
        ],
        'timeout': 30000,
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    response = requests.post(api_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result['entries']['data'][0]['status'] == 'Success', None
    else:
        return None, f'Error: {response.status_code}'


vocalhost.API_KEY = settings.VOCALHOST_API


def generate_tags(input_data):
    data = {
        'message': input_data,
        'limit': 4
    }
    message = json.dumps(data)

    response = vocalhost.Request.send(message=message, receiver_id='tags_1')
    response = json.loads(response.text)
    tags = response.get('tags')
    tags = ', '.join(tags).replace(',', ', ')
    return tags


def summarize(input_data):
    data = {
        'message': input_data,
        'limit': 528
    }
    message = json.dumps(data)

    response = vocalhost.Request.send(message=message, receiver_id='summary_1', timeout=120)
    response = json.loads(response.text)
    summary = response.get('summary')
    return summary


def gpt_neo_2_7_B(input_data):
    data = {
        'message': input_data,
        'limit': 64
    }
    message = json.dumps(data)

    response = vocalhost.Request.send(message=message, receiver_id='gpt-neo-2.7B', timeout=120)
    response = json.loads(response.text)
    summary = response.get('generation')
    return summary
