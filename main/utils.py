import io
import json

import requests
import vocalhost
from PIL import Image
from sendgrid import Mail, SendGridAPIClient

from djangoProject1 import settings

SUPPORTED_LANGUAGES = [
    'af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs', 'bg', 'ca', 'ceb', 'ny',
    'zh', 'zh-CN', 'zh-TW', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl', 'en', 'eo', 'et', 'ee', 'tl', 'fil', 'fi',
    'fr', 'fy', 'gl', 'lg', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'iw', 'he', 'hi', 'hmn', 'hu', 'is',
    'ig', 'ilo', 'id', 'ga', 'it', 'ja', 'jw', 'jv', 'kn', 'kk', 'km', 'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky',
    'lo', 'la', 'lv', 'ln', 'lt', 'lb', 'mk', 'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-Mtei', 'lus', 'mn',
    'my', 'ne', 'nso', 'no', 'or', 'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'sr',
    'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts',
    'tr', 'tk', 'ak', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu',
]


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


def send_email(subject, message, to_email):
    subject = subject
    message = message
    from_email = 'ReiserX <{}>'.format(settings.DEFAULT_FROM_EMAIL)

    mail = Mail(from_email=from_email, subject=subject, to_emails=to_email, html_content=message)
    try:
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        sg.send(mail)
    except Exception as e:
        pass