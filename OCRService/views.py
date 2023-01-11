import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def process(request):
    if request.method == 'POST':
        if request.headers.get("Authorization")  == "check":
            data = json.loads(request.body)
            result = ''
            try:
                result = execute_user_code(data.get('code'))
            except Exception as e:
                # to return error in the code
                result = e
            return HttpResponse(result)
        else:
            return HttpResponse("You are not allowed")

from RestrictedPython import safe_builtins, compile_restricted

_SAFE_MODULES = frozenset(("math",))


def _safe_import(name, *args, **kwargs):
    if name not in _SAFE_MODULES:
        raise Exception(f"Your are not allowed to import {name!r}")
    return __import__(name, *args, **kwargs)


def execute_user_code(user_code, *args, **kwargs):
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "__import__": _safe_import,
        },
    }

    try:
        byte_code = compile_restricted(
            user_code, filename="<user_code>", mode="exec")
    except SyntaxError:
        # syntax error in the sandboxed code
        raise

    try:
        exec(byte_code, my_globals)
    except BaseException:
        # runtime error (probably) in the sandboxed code
        raise


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
