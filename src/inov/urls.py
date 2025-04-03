"""inov URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import api
# from api.views import AlimentAPIView, SinistreAPIView

from configurations import views
from api import views as api_views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


customUrl = []

# if settings.DEBUG:
customUrl += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
# Ici nous créons notre routeur
router = routers.SimpleRouter()
# Puis lui déclarons une url basée sur le mot clé ‘category’ et notre view

# afin que l’url générée soit celle que nous souhaitons ‘/api/aliment/’
# router.register('aliment', AlimentAPIView, basename='aliment')


urlpatterns = customUrl + [
    path('admin/clearcache/', include('clearcache.urls')),
    path('api/', include('api.urls')),

    path('api/token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/status_sinistre', api_views.get_status_sinistre),
    path('api/assure_infos', include(router.urls)),
    path("i18n/", include("django.conf.urls.i18n")),
    path('comptabilite/', include('comptabilite.urls')),
    path('grh/', include('grh.urls')),
    path('sinistre/', include('sinistre.urls')),
    path('production/', include('production.urls')),
    path('configurations/', include('configurations.urls')),
    path('analysecontrole/', include('analysecontrole.urls')),
    path('accounts/profile/', views.redirecttohome),
    path('accounts/login/', views.redirecttohome),
    path('password_change/', views.custom_password_change, name='password_change'),
    path("", admin.site.urls),
    

    
]


# if not settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#


