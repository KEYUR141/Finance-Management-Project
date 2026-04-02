from django.shortcuts import render
from rest_framework import status, viewsets, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, action
from rest_framework.views import APIView
#Aurhentication
from .authentication import UserAuthService

from .models import FinancialRecords, UserProfile
from .serializers import FinancialRecordsSerializer, UserProfileSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from .permissions import IsAdminOrNot, IsAnalystOrAbove, IsViewerOrAbove
from rest_framework.authentication import TokenAuthentication
import logging

logger = logging.getLogger(__name__)

class AuthenticationViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            logger.warning("Missing email/username or password in login request")
            return Response({"error": "Email and password required"}, status=400)

        try:
            res = UserAuthService.login(email, password)
            return Response(res, status=200)

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({"error": str(e)}, status=401)





class FincancialRecordsViewSet(viewsets.ModelViewSet):
    queryset = FinancialRecords.objects.filter(is_deleted=False)
    serializer_class = FinancialRecordsSerializer
    permission_classes = [IsAuthenticated, IsAnalystOrAbove]

    @action(detail=False, methods=['get'], url_path='records', permission_classes=[IsAuthenticated, IsAnalystOrAbove])
    def get_records(self, request):
        try:
            records_data = self.queryset
            serializer = self.serializer_class(records_data, many=True)
            return Response({
                'Status': True,
                'Message': "Financial Records Retrieved",
                'data' : serializer.data
            })
        except Exception as e:
            return Response({
                'Status': 'Failed',
                'Message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['post'], url_path='add-record', permission_classes=[IsAuthenticated, IsAdminOrNot])
    def add_records(self,request):
        try:
            data = request.data
            serializer_data = self.serializer_class(data=data)
            if serializer_data.is_valid():
                serializer_data.save()
                return Response({
                    'Status': True,
                    'Message': "Financial Record Added",
                    'data' : serializer_data.data
                })
            return Response({
                'Status': 'Failed',
                'Message': serializer_data.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'Status': 'Failed',
                'Message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



