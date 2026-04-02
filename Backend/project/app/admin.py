from django.contrib import admin
from .models import UserProfile, FinancialRecords
# Register your models here.

admin.site.register({UserProfile, FinancialRecords})
