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

#Essnetials for the dashboard KPIs
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

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

    @action(detail=False, methods=['get'], url_path='records', permission_classes=[IsAuthenticated, IsViewerOrAbove])
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
    
    @action(detail=False, methods=['patch'], url_path='update-record', permission_classes=[IsAuthenticated, IsAdminOrNot])
    def update_records(self, request):
        try:
            uuid = request.data.get('uuid')
            data = request.data
            record = FinancialRecords.objects.get(uuid=uuid)
            serializer_data = self.serializer_class(record, data=data, partial=True)
            if serializer_data.is_valid():
                serializer_data.save()
                return Response({
                    'Status': True,
                    'Message': "Financial Record Updated",
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
    
    @action(detail=False, methods=['delete'], url_path='delete-record', permission_classes=[IsAuthenticated, IsAdminOrNot])
    def delete_records(self, request):
        try:
            instance = request.data.get('uuid')
            record = FinancialRecords.objects.get(uuid=instance)
            record.is_deleted = True
            record.save()
            return Response({
                'Status': True,
                'Message': "Financial Record Deleted",
            })
        except Exception as e:
            return Response({
                'Status': 'Failed',
                'Message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class DashboardKPIView(APIView):

    permission_classes = [IsAuthenticated, IsViewerOrAbove]

    def get(self, request):
        try:
            # TIER 1: CORE KPIs
            total_income = FinancialRecords.objects.filter(
                type_of_record='income', is_deleted=False
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            total_expense = FinancialRecords.objects.filter(
                type_of_record='expense', is_deleted=False
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            net_balance = total_income - total_expense

            # CURRENT MONTH METRICS 
            now = timezone.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            current_month_income = FinancialRecords.objects.filter(
                type_of_record='income',
                is_deleted=False,
                date__gte=month_start
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            current_month_expense = FinancialRecords.objects.filter(
                type_of_record='expense',
                is_deleted=False,
                date__gte=month_start
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            current_month_balance = current_month_income - current_month_expense

            # TIER 2: CATEGORY BREAKDOWN
            category_breakdown = []
            categories = FinancialRecords.objects.filter(
                is_deleted=False
            ).values('category', 'type_of_record').annotate(
                count=Count('uuid'),
                total_amount=Sum('amount')
            ).order_by('-total_amount')
            
            for cat in categories:
                category_breakdown.append({
                    'category': cat['category'],
                    'type': cat['type_of_record'],
                    'count': cat['count'],
                    'amount': float(cat['total_amount'] or 0)
                })

            # TOP 5 CATEGORIES BY AMOUNT
            top_categories = []
            top_cats = FinancialRecords.objects.filter(
                is_deleted=False
            ).values('category').annotate(
                total_amount=Sum('amount')
            ).order_by('-total_amount')[:5]
            
            for cat in top_cats:
                top_categories.append({
                    'category': cat['category'],
                    'amount': float(cat['total_amount'] or 0)
                })

            # RECENT TRANSACTIONS
            recent_transactions = []
            recent_records = FinancialRecords.objects.filter(
                is_deleted=False
            ).order_by('-date')[:10]
            
            for record in recent_records:
                recent_transactions.append({
                    'date': str(record.date),
                    'category': record.category,
                    'type': record.type_of_record,
                    'amount': float(record.amount),
                    'notes': record.notes or ''
                })

            # INCOME vs EXPENSE RATIO 
            total_transactions = total_income + total_expense
            if total_transactions > 0:
                income_percentage = (total_income / total_transactions) * 100
                expense_percentage = (total_expense / total_transactions) * 100
            else:
                income_percentage = 0
                expense_percentage = 0

            # STATISTICS 
            total_record_count = FinancialRecords.objects.filter(
                is_deleted=False
            ).count()
            
            avg_transaction = 0
            if total_record_count > 0:
                total_all = FinancialRecords.objects.filter(
                    is_deleted=False
                ).aggregate(total=Sum('amount'))['total'] or 0
                avg_transaction = float(total_all / total_record_count)

            # Most frequent category
            most_frequent = FinancialRecords.objects.filter(
                is_deleted=False
            ).values('category').annotate(
                count=Count('uuid')
            ).order_by('-count').first()
            most_frequent_category = most_frequent['category'] if most_frequent else 'N/A'

            # RETURN RESPONSE
            return Response({
                'Status': True,
                'Message': "Dashboard Summary Retrieved",
                'data': {
                    'kpis': {
                        'total_income': float(total_income),
                        'total_expense': float(total_expense),
                        'net_balance': float(net_balance),
                        'current_month_income': float(current_month_income),
                        'current_month_expense': float(current_month_expense),
                        'current_month_balance': float(current_month_balance)
                    },
                    'category_breakdown': category_breakdown,
                    'top_categories': top_categories,
                    'recent_transactions': recent_transactions,
                    'ratios': {
                        'income_percentage': round(income_percentage, 2),
                        'expense_percentage': round(expense_percentage, 2)
                    },
                    'statistics': {
                        'total_transactions': total_record_count,
                        'average_transaction_amount': round(avg_transaction, 2),
                        'most_frequent_category': most_frequent_category
                    }
                }
            })
        except Exception as e:
            logger.error(f"Dashboard KPI Error: {str(e)}")
            return Response({
                'Status': False,
                'Message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



