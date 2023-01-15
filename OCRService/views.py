import json
import sys

import requests
from RestrictedPython import safe_builtins
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def process(request):
    if request.method == 'POST':
        if request.headers.get("Authorization") == "check":
            data = json.loads(request.body)
            result = {"response": ''}
            try:
                result['response'] = execute_user_code(data.get('code'))
            except Exception as e:
                # to return error in the code
                result['response'] = e
            return JsonResponse(result, content_type='application/json')
        else:
            return HttpResponse("Permission denied")


_SAFE_MODULES = frozenset(("math",))


def _safe_import(name, *args, **kwargs):
    if name not in _SAFE_MODULES:
        raise Exception(f"You are are not allowed to import {name!r}")
    return __import__(name, *args, **kwargs)


def execute_user_code(user_code, *args, **kwargs):
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "print": print,
            "__import__": _safe_import
        },
    }
    try:
        byte_code = compile(user_code, filename="<user_code>", mode="exec")
    except SyntaxError:
        raise
    try:
        original_stdout = sys.stdout
        sys.stdout = open('file.txt', 'w')

        exec(byte_code, my_globals, {})

        sys.stdout.close()

        sys.stdout = original_stdout  # reset the standard output to its original value

        # finally read output from file and save in output variable

        output = open('file.txt', 'r').read()
    except BaseException as e:
        sys.stdout = original_stdout
        output = e
        # runtime error (probably) in the sandboxed code
    return output


def index(request):
    return render(request, 'codeEditor.html')


def runcode(request):
    if request.method == 'POST':
        codeareadata = request.POST['codearea']
        try:
            result = execute_user_code(codeareadata)
        except Exception as e:
            # to return error in the code
            result = e
    return render(request, 'codeEditor.html', {"code": codeareadata, "output": result})


@csrf_exempt
def scan_document(request):
    if request.method == 'POST':
        if request.headers.get("Authorization") == "check":
            data = json.loads(request.body)

            response = process_vision(data.get("image"))
            return HttpResponse(response)
        else:
            return HttpResponse("Permission denied")


def process_vision(code):

    data = {
        "requests": [
            {
                "image": {
                    "content": code
                },
                "features": [
                    {
                        "type": "DOCUMENT_TEXT_DETECTION"
                    }
                ],
                "imageContext": {
                    "languageHints": ["en-t-i0-handwrit"]
                }
            }
        ]
    }
    r = requests.post(URL, json=data)
    return r.text
