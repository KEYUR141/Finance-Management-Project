"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.views.generic import RedirectView
from app.template_views import login_view, dashboard_view, records_view, profile_view, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('app.urls')),
    
    # Template Views
    path('login-page/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('records/', records_view, name='records'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    
    path('', RedirectView.as_view(url='login-page/', permanent=False)),
]
