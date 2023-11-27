from django.http import HttpResponseForbidden
from django.urls import reverse


class SuperuserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_superuser and request.path_info.startswith('/Alizeh/'):
            message = (
                "Access denied. Superuser required. "
                f"Login to continue <a href='{reverse('login_page')}'>Login</a>."
            )
            return HttpResponseForbidden(message)
        return self.get_response(request)