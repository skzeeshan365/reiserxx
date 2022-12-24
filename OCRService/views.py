import io
import json
import os

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.cloud import vision


@csrf_exempt
def process(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        process_request(data.get('image'))
    return HttpResponse('received_json_data')


def process_request(data):

    # calling up google vision json file
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'D:\Downloads\test-372219-215a3e9402e5.json'

    client = vision.ImageAnnotatorClient()

    content = data

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image, image_context={"language_hints": ["en-t-i0-handwrit"]})

    print(response.full_text_annotation.text)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))