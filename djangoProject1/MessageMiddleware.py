from django.http import HttpResponseForbidden


class SuperuserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_superuser and request.path_info.startswith('/message/'):
            return HttpResponseForbidden("Access denied. Superuser required.")
        return self.get_response(request)