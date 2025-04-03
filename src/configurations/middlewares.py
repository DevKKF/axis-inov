import datetime
from pprint import pprint

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django_dump_die.middleware import dd

from inov import settings
from shared.enum import PasswordType

from django.utils import timezone


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        pprint('ForcePasswordChangeMiddleware')

        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Enregistre la dernière page visitée dans la session
            request.session['last_visited'] = request.path
            request.session['last_ip_adress'] = request.META.get('REMOTE_ADDR')
            request.session['last_visit_time'] = datetime.datetime.now().isoformat()  # Enregistre la date au format ISO

        if request.user.is_authenticated and request.user.last_login is None and request.user.password_type == PasswordType.DEFAULT:
            pprint("Connected user use default password")

            if not request.path.startswith('/password_change/'):
                return redirect('admin:password_change')

        response = self.get_response(request)
        return response


class AnonymousUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifie si l'utilisateur est anonyme
        '''if request.user.is_anonymous and not request.path.startswith('/login'):
            pprint("-- ANONYME USER CONNECTED, REDIRECTING TO LOGIN PAGE")

            # Redirige vers la page de connexion
            login_url = "/login"  # Assurez-vous d'avoir une URL nommée 'login'

            return redirect(login_url)
        '''
        response = self.get_response(request)
        return response
    
    
    
    
#  2fa


from django.http import HttpResponseRedirect
from django.urls import reverse

##################################
class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.session.get('is_verified', False) and not request.path_info.startswith('/grh/'):
            if request.path != reverse('verify_code'):
                return HttpResponseRedirect(reverse('verify_code'))

        response = self.get_response(request)
        return response

