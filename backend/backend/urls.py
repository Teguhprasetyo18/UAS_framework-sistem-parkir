"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.authtoken.views import obtain_auth_token
from parkir.views import KendaraanViewSet

# Simple home view
def home(request):
    return JsonResponse({
        'message': 'Django Parkir API is running!',
        'endpoints': {
            'admin': '/admin/',
            'api_token_auth': '/api/token-auth/',
            'api_root': '/api/',
            'kendaraan': '/api/kendaraan/',
            'parkir': '/api/parkir/',
        }
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/token-auth/', views.obtain_auth_token, name='api_token_auth'),
    path('api/', include('parkir.urls')),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/kendaraan/', KendaraanViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/kendaraan/<int:pk>/', KendaraanViewSet.as_view({'put': 'update'})),

]
