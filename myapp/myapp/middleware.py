# middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path == reverse('login'):
            return redirect(reverse('index'))  # Ganti 'index' dengan nama url beranda Anda
        response = self.get_response(request)
        return response
