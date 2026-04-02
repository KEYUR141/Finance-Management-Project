from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile
import json


def login_view(request):
    """Render login page"""
    return render(request, 'login.html')


def dashboard_view(request):
    """Render dashboard page"""
    return render(request, 'dashboard.html')


def records_view(request):
    """Render financial records page"""
    return render(request, 'records.html')


def profile_view(request):
    """Render user profile page"""
    return render(request, 'profile.html')


def logout_view(request):
    """Logout user and redirect to login"""
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, uuid):
    """API endpoint to get user profile by UUID"""
    try:
        user_profile = UserProfile.objects.get(uuid=uuid)
        return Response({
            'uuid': str(user_profile.uuid),
            'user_name': user_profile.user_name,
            'email': user_profile.email,
            'role': user_profile.role,
            'is_active': user_profile.is_active,
            'created_at': user_profile.created_at,
            'updated_at': user_profile.updated_at,
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
