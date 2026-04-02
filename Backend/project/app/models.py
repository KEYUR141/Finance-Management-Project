from django.db import models
from django.contrib.auth.models import User
import uuid



# Create your models here.
class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class UserProfile(BaseModel):
    user_name = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    email = models.EmailField(unique=True)
    role_category = [
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=role_category, default='viewer')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user_name} - {self.email} - {self.first_name} {self.last_name}"

class FinancialRecords(BaseModel):
    created_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL,null=True,related_name='financial_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    record_type_category = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    type_of_record = models.CharField(max_length=20, choices=record_type_category, default='expense')
    category_choices = [
        ('salary', 'Salary'),
        ('food', 'Food'),
        ('rent', 'Rent'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=category_choices, default='other')
    date = models.DateField()
    notes = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.created_by} - {self.amount} - {self.type_of_record} - {self.category}"


