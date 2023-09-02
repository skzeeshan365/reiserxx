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

language_list = [{'code': 'af', 'name': 'Afrikaans'}, {'code': 'sq', 'name': 'Albanian'},
                 {'code': 'am', 'name': 'Amharic'}, {'code': 'ar', 'name': 'Arabic'},
                 {'code': 'hy', 'name': 'Armenian'}, {'code': 'as', 'name': 'Assamese'},
                 {'code': 'ay', 'name': 'Aymara'}, {'code': 'az', 'name': 'Azerbaijani'},
                 {'code': 'bm', 'name': 'Bambara'}, {'code': 'eu', 'name': 'Basque'},
                 {'code': 'be', 'name': 'Belarusian'}, {'code': 'bn', 'name': 'Bengali'},
                 {'code': 'bho', 'name': 'Bhojpuri'}, {'code': 'bs', 'name': 'Bosnian'},
                 {'code': 'bg', 'name': 'Bulgarian'}, {'code': 'ca', 'name': 'Catalan'},
                 {'code': 'ceb', 'name': 'Cebuano'}, {'code': 'ny', 'name': 'Chichewa'},
                 {'code': 'zh', 'name': 'Chinese (Simplified)'}, {'code': 'zh-CN', 'name': 'Chinese (Simplified)'},
                 {'code': 'zh-TW', 'name': 'Chinese (Traditional)'}, {'code': 'co', 'name': 'Corsican'},
                 {'code': 'hr', 'name': 'Croatian'}, {'code': 'cs', 'name': 'Czech'}, {'code': 'da', 'name': 'Danish'},
                 {'code': 'dv', 'name': 'Divehi'}, {'code': 'doi', 'name': 'Dogri'}, {'code': 'nl', 'name': 'Dutch'},
                 {'code': 'en', 'name': 'English'}, {'code': 'eo', 'name': 'Esperanto'},
                 {'code': 'et', 'name': 'Estonian'}, {'code': 'ee', 'name': 'Ewe'}, {'code': 'tl', 'name': 'Filipino'},
                 {'code': 'fil', 'name': 'Filipino'}, {'code': 'fi', 'name': 'Finnish'},
                 {'code': 'fr', 'name': 'French'}, {'code': 'fy', 'name': 'Frisian'},
                 {'code': 'gl', 'name': 'Galician'}, {'code': 'lg', 'name': 'Ganda'},
                 {'code': 'ka', 'name': 'Georgian'}, {'code': 'de', 'name': 'German'}, {'code': 'el', 'name': 'Greek'},
                 {'code': 'gn', 'name': 'Guarani'}, {'code': 'gu', 'name': 'Gujarati'},
                 {'code': 'ht', 'name': 'Haitian Creole'}, {'code': 'ha', 'name': 'Hausa'},
                 {'code': 'haw', 'name': 'Hawaiian'}, {'code': 'iw', 'name': 'Hebrew'},
                 {'code': 'he', 'name': 'Hebrew'}, {'code': 'hi', 'name': 'Hindi'}, {'code': 'hmn', 'name': 'Hmong'},
                 {'code': 'hu', 'name': 'Hungarian'}, {'code': 'is', 'name': 'Icelandic'},
                 {'code': 'ig', 'name': 'Igbo'}, {'code': 'ilo', 'name': 'Iloko'}, {'code': 'id', 'name': 'Indonesian'},
                 {'code': 'ga', 'name': 'Irish Gaelic'}, {'code': 'it', 'name': 'Italian'},
                 {'code': 'ja', 'name': 'Japanese'}, {'code': 'jw', 'name': 'Javanese'},
                 {'code': 'jv', 'name': 'Javanese'}, {'code': 'kn', 'name': 'Kannada'},
                 {'code': 'kk', 'name': 'Kazakh'}, {'code': 'km', 'name': 'Khmer'},
                 {'code': 'rw', 'name': 'Kinyarwanda'}, {'code': 'gom', 'name': 'Konkani'},
                 {'code': 'ko', 'name': 'Korean'}, {'code': 'kri', 'name': 'Krio'},
                 {'code': 'ku', 'name': 'Kurdish (Kurmanji)'}, {'code': 'ckb', 'name': 'Kurdish (Sorani)'},
                 {'code': 'ky', 'name': 'Kyrgyz'}, {'code': 'lo', 'name': 'Lao'}, {'code': 'la', 'name': 'Latin'},
                 {'code': 'lv', 'name': 'Latvian'}, {'code': 'ln', 'name': 'Lingala'},
                 {'code': 'lt', 'name': 'Lithuanian'}, {'code': 'lb', 'name': 'Luxembourgish'},
                 {'code': 'mk', 'name': 'Macedonian'}, {'code': 'mai', 'name': 'Maithili'},
                 {'code': 'mg', 'name': 'Malagasy'}, {'code': 'ms', 'name': 'Malay'},
                 {'code': 'ml', 'name': 'Malayalam'}, {'code': 'mt', 'name': 'Maltese'},
                 {'code': 'mi', 'name': 'Maori'}, {'code': 'mr', 'name': 'Marathi'},
                 {'code': 'mni-Mtei', 'name': 'Meiteilon (Manipuri)'}, {'code': 'lus', 'name': 'Mizo'},
                 {'code': 'mn', 'name': 'Mongolian'}, {'code': 'my', 'name': 'Myanmar (Burmese)'},
                 {'code': 'ne', 'name': 'Nepali'}, {'code': 'nso', 'name': 'Northern Sotho'},
                 {'code': 'no', 'name': 'Norwegian'}, {'code': 'or', 'name': 'Odia (Oriya)'},
                 {'code': 'om', 'name': 'Oromo'}, {'code': 'ps', 'name': 'Pashto'}, {'code': 'fa', 'name': 'Persian'},
                 {'code': 'pl', 'name': 'Polish'}, {'code': 'pt', 'name': 'Portuguese'},
                 {'code': 'pa', 'name': 'Punjabi'}, {'code': 'qu', 'name': 'Quechua'},
                 {'code': 'ro', 'name': 'Romanian'}, {'code': 'ru', 'name': 'Russian'},
                 {'code': 'sm', 'name': 'Samoan'}, {'code': 'sa', 'name': 'Sanskrit'},
                 {'code': 'gd', 'name': 'Scots Gaelic'}, {'code': 'sr', 'name': 'Serbian'},
                 {'code': 'st', 'name': 'Sesotho'}, {'code': 'sn', 'name': 'Shona'}, {'code': 'sd', 'name': 'Sindhi'},
                 {'code': 'si', 'name': 'Sinhala'}, {'code': 'sk', 'name': 'Slovak'},
                 {'code': 'sl', 'name': 'Slovenian'}, {'code': 'so', 'name': 'Somali'},
                 {'code': 'es', 'name': 'Spanish'}, {'code': 'su', 'name': 'Sundanese'},
                 {'code': 'sw', 'name': 'Swahili'}, {'code': 'sv', 'name': 'Swedish'}, {'code': 'tg', 'name': 'Tajik'},
                 {'code': 'ta', 'name': 'Tamil'}, {'code': 'tt', 'name': 'Tatar'}, {'code': 'te', 'name': 'Telugu'},
                 {'code': 'th', 'name': 'Thai'}, {'code': 'ti', 'name': 'Tigrinya'}, {'code': 'ts', 'name': 'Tsonga'},
                 {'code': 'tr', 'name': 'Turkish'}, {'code': 'tk', 'name': 'Turkmen'}, {'code': 'ak', 'name': 'Twi'},
                 {'code': 'uk', 'name': 'Ukrainian'}, {'code': 'ur', 'name': 'Urdu'}, {'code': 'ug', 'name': 'Uyghur'},
                 {'code': 'uz', 'name': 'Uzbek'}, {'code': 'vi', 'name': 'Vietnamese'}, {'code': 'cy', 'name': 'Welsh'},
                 {'code': 'xh', 'name': 'Xhosa'}, {'code': 'yi', 'name': 'Yiddish'}, {'code': 'yo', 'name': 'Yoruba'},
                 {'code': 'zu', 'name': 'Zulu'}]


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