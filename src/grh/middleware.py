# middleware.py

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_urls = ['/grh/formulaire_enrolement/', '/grh/enrolement/','/grh/password_reset/', '/grh/verify_codes/']
        if not request.user.is_authenticated and not request.path_info.startswith('/grh/login'):
            if any(request.path_info.startswith(url) for url in excluded_urls):
                return self.get_response(request)
            elif request.path_info.startswith('/grh/'):
                return redirect(reverse('grh.login'))
        
        response = self.get_response(request)
        return response
    
    




