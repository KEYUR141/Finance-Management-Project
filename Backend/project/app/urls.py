from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

#Importing Views Logic
from .views import AuthenticationViewSet, FincancialRecordsViewSet

router = DefaultRouter()





urlpatterns = [
    path('', include(router.urls)),
    path('login/', AuthenticationViewSet.as_view(), name='login')
]
