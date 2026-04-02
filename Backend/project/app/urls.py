from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

#Importing Views Logic
from .views import AuthenticationViewSet, FincancialRecordsViewSet
from .template_views import get_user_profile

router = DefaultRouter()
router.register(r'financial-records', FincancialRecordsViewSet, basename='financial-records')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', AuthenticationViewSet.as_view(), name='api-login'),
    path('users/<uuid:uuid>/', get_user_profile, name='get-user-profile'),
]
