"""
WSGI config for inov project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys

# Add this line
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inov.settings')

application = get_wsgi_application()
