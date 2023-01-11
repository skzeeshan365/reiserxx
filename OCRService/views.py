import json
import sys
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from RestrictedPython import safe_builtins

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


_SAFE_MODULES = frozenset("math")

def _safe_import(name, *args, **kwargs):
    if name not in _SAFE_MODULES:
        raise Exception(f"You are are not allowed to import {name!r}")
    return __import__(name, *args, **kwargs)


def execute_user_code(user_code, *args, **kwargs):
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "__import__": _safe_import,
            "_print_": print,
            "print": print,
        },
    }
    byte_code = 0
    try:
        byte_code = compile(user_code, filename="<user_code>", mode="exec")
    except SyntaxError as e:
        output = e
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
        result = ''
        try:
            result = execute_user_code(codeareadata)
        except Exception as e:
            # to return error in the code
            result = e
    return render(request, 'codeEditor.html', {"code": codeareadata, "output": result})