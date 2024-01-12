"""copa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import re

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from django.views.static import serve


def index(request):
    return JsonResponse({'status': 'running'})


urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('mirror/', include('mirror.urls', 'mirror')),
]


urlpatterns.append(re_path(
    '^' + re.escape(settings.STATIC_URL.lstrip('/')) + '(?P<path>.*)$',
    serve,
    {'document_root': settings.STATIC_ROOT}))

# urlpatterns.append(re_path(
#     '^' + 'docs' + '(?P<path>.*)$',
#     serve,
#     {'document_root': 'docs'}))


