"""
URL configuration for money_manage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from collections import OrderedDict
from django.urls import re_path, path, include

from rest_framework.routers import APIRootView

api_root_dict = OrderedDict()
api_root_dict['audio'] = 'audio-root'
root_view = APIRootView.as_view(api_root_dict=api_root_dict)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        re_path(r'^$', root_view, name='api-root'),
        path('accounts/', include('account.urls')),
        path('money/', include('money.urls')),
    ])),
]
