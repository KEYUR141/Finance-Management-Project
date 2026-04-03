from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

from .models import UserProfile, FinancialRecords


class TestUserProfileModel(TestCase):
    """Unit tests for UserProfile model"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_user_profile_creation(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            email='test@example.com',
            user_name='testuser',
            password_hash='hashed_password_123',
            role='admin',
            is_active=True
        )
        
        self.assertIsNotNone(profile.uuid)
        self.assertEqual(profile.email, 'test@example.com')
        self.assertEqual(profile.role, 'admin')
        self.assertTrue(profile.is_active)
    
    def test_user_profile_unique_email(self):
        """Test that email must be unique"""
        UserProfile.objects.create(
            user=self.user,
            email='test@example.com',
            user_name='testuser',
            password_hash='hash',
            role='viewer'
        )
        
        # Try to create another with same email
        new_user = User.objects.create_user(
            username='different',
            email='different@example.com'
        )
        
        with self.assertRaises(Exception):
            UserProfile.objects.create(
                user=new_user,
                email='test@example.com',  # Duplicate
                user_name='newuser',
                password_hash='hash',
                role='viewer'
            )
    
    def test_user_profile_unique_username(self):
        """Test that username must be unique"""
        UserProfile.objects.create(
            user=self.user,
            email='test@example.com',
            user_name='testuser',
            password_hash='hash',
            role='viewer'
        )
        
        # Try to create another with same username
        new_user = User.objects.create_user(
            username='different',
            email='different@example.com'
        )
        
        with self.assertRaises(Exception):
            UserProfile.objects.create(
                user=new_user,
                email='different@example.com',
                user_name='testuser',  # Duplicate
                password_hash='hash',
                role='viewer'
            )
    
    def test_user_profile_timestamps(self):
        """Test that created_at and updated_at are set"""
        profile = UserProfile.objects.create(
            user=self.user,
            email='test@example.com',
            user_name='testuser',
            password_hash='hash',
            role='admin'
        )
        
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_all_roles_can_be_created(self):
        """Test that all roles can be created"""
        roles = ['viewer', 'analyst', 'admin']
        
        for i, role in enumerate(roles):
            user = User.objects.create_user(
                username=f'{role}_user_{i}',
                email=f'{role}_{i}@example.com'
            )
            profile = UserProfile.objects.create(
                user=user,
                email=f'{role}_{i}@example.com',
                user_name=f'{role}_user_{i}',
                password_hash='hash',
                role=role
            )
            self.assertEqual(profile.role, role)


class TestFinancialRecordsModel(TestCase):
    """Unit tests for FinancialRecords model"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            email='admin@example.com',
            user_name='admin',
            password_hash='hash',
            role='admin'
        )
    
    def test_create_financial_record(self):
        """Test creating a financial record"""
        record = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('50000.00'),
            date='2026-04-03',
            notes='Test salary'
        )
        
        self.assertIsNotNone(record.uuid)
        self.assertEqual(record.type_of_record, 'income')
        self.assertEqual(record.category, 'salary')
        self.assertEqual(record.amount, Decimal('50000.00'))
        self.assertFalse(record.is_deleted)
    
    def test_soft_delete(self):
        """Test soft delete functionality"""
        record = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('50000.00'),
            date='2026-04-03'
        )
        
        record.is_deleted = True
        record.save()
        
        # Record still exists in DB
        existing = FinancialRecords.objects.filter(uuid=record.uuid).first()
        self.assertIsNotNone(existing)
        # But is marked as deleted
        self.assertTrue(record.is_deleted)
    
    def test_financial_record_uniqueness(self):
        """Test that records have unique UUIDs"""
        record1 = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('50000.00'),
            date='2026-04-03'
        )
        
        record2 = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('50000.00'),
            date='2026-04-03'
        )
        
        # UUIDs should be different
        self.assertNotEqual(record1.uuid, record2.uuid)
    
    def test_valid_categories(self):
        """Test that valid categories work"""
        valid_categories = ['salary', 'food', 'rent', 'investment', 'other']
        
        for category in valid_categories:
            record = FinancialRecords.objects.create(
                created_by=self.profile,
                type_of_record='income',
                category=category,
                amount=Decimal('1000.00'),
                date='2026-04-03'
            )
            self.assertEqual(record.category, category)
    
    def test_valid_record_types(self):
        """Test that record types work"""
        record_income = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('1000.00'),
            date='2026-04-03'
        )
        self.assertEqual(record_income.type_of_record, 'income')
        
        record_expense = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='expense',
            category='food',
            amount=Decimal('500.00'),
            date='2026-04-03'
        )
        self.assertEqual(record_expense.type_of_record, 'expense')
    
    def test_decimal_amounts(self):
        """Test that decimal amounts are stored correctly"""
        amounts = [Decimal('100.00'), Decimal('1000.50'), Decimal('99999.99')]
        
        for amount in amounts:
            record = FinancialRecords.objects.create(
                created_by=self.profile,
                type_of_record='income',
                category='salary',
                amount=amount,
                date='2026-04-03'
            )
            self.assertEqual(record.amount, amount)
    
    def test_optional_notes(self):
        """Test that notes are optional"""
        # With notes
        record_with_notes = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('1000.00'),
            date='2026-04-03',
            notes='Some notes'
        )
        self.assertEqual(record_with_notes.notes, 'Some notes')
        
        # Without notes
        record_without_notes = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('1000.00'),
            date='2026-04-03'
        )
        self.assertEqual(record_without_notes.notes, '')
    
    def test_record_timestamps(self):
        """Test that created_at and updated_at are set"""
        record = FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('1000.00'),
            date='2026-04-03'
        )
        
        self.assertIsNotNone(record.created_at)
        self.assertIsNotNone(record.updated_at)


class TestRecordFiltering(TestCase):
    """Test filtering financial records"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            email='admin@example.com',
            user_name='admin',
            password_hash='hash',
            role='admin'
        )
        
        # Create multiple records
        FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('100000.00'),
            date='2026-04-03'
        )
        
        FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='expense',
            category='food',
            amount=Decimal('5000.00'),
            date='2026-04-03'
        )
        
        FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='investment',
            amount=Decimal('50000.00'),
            date='2026-04-02'
        )
    
    def test_filter_by_type(self):
        """Test filtering by record type"""
        income_records = FinancialRecords.objects.filter(type_of_record='income')
        self.assertEqual(income_records.count(), 2)
        
        expense_records = FinancialRecords.objects.filter(type_of_record='expense')
        self.assertEqual(expense_records.count(), 1)
    
    def test_filter_by_category(self):
        """Test filtering by category"""
        salary_records = FinancialRecords.objects.filter(category='salary')
        self.assertEqual(salary_records.count(), 1)
        
        investment_records = FinancialRecords.objects.filter(category='investment')
        self.assertEqual(investment_records.count(), 1)
    
    def test_filter_by_date(self):
        """Test filtering by date"""
        records_on_04_03 = FinancialRecords.objects.filter(date='2026-04-03')
        self.assertEqual(records_on_04_03.count(), 2)
        
        records_on_04_02 = FinancialRecords.objects.filter(date='2026-04-02')
        self.assertEqual(records_on_04_02.count(), 1)
    
    def test_filter_by_amount_range(self):
        """Test filtering by amount range"""
        high_amount = FinancialRecords.objects.filter(amount__gte=Decimal('50000.00'))
        self.assertEqual(high_amount.count(), 2)
        
        low_amount = FinancialRecords.objects.filter(amount__lt=Decimal('50000.00'))
        self.assertEqual(low_amount.count(), 1)
    
    def test_exclude_soft_deleted(self):
        """Test that soft-deleted records can be filtered"""
        # Get first record and mark as deleted
        record = FinancialRecords.objects.first()
        record.is_deleted = True
        record.save()
        
        # When filtering without explicit is_deleted filter, shows all
        all_records = FinancialRecords.objects.all()
        self.assertEqual(all_records.count(), 3)
        
        # Can filter to exclude
        active_records = FinancialRecords.objects.filter(is_deleted=False)
        self.assertEqual(active_records.count(), 2)


class TestDataAggregation(TestCase):
    """Test aggregating financial data"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            email='admin@example.com',
            user_name='admin',
            password_hash='hash',
            role='admin'
        )
        
        # Create records for aggregation testing
        FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='salary',
            amount=Decimal('100000.00'),
            date='2026-04-03'
        )
        
        FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='income',
            category='investment',
            amount=Decimal('50000.00'),
            date='2026-04-03'
        )
        
        FinancialRecords.objects.create(
            created_by=self.profile,
            type_of_record='expense',
            category='food',
            amount=Decimal('5000.00'),
            date='2026-04-03'
        )
    
    def test_total_income_sum(self):
        """Test summing total income"""
        from django.db.models import Sum
        
        total_income = FinancialRecords.objects.filter(
            type_of_record='income'
        ).aggregate(Sum('amount'))['amount__sum']
        
        self.assertEqual(total_income, Decimal('150000.00'))
    
    def test_total_expense_sum(self):
        """Test summing total expenses"""
        from django.db.models import Sum
        
        total_expense = FinancialRecords.objects.filter(
            type_of_record='expense'
        ).aggregate(Sum('amount'))['amount__sum']
        
        self.assertEqual(total_expense, Decimal('5000.00'))
    
    def test_category_count(self):
        """Test counting by category"""
        salary_count = FinancialRecords.objects.filter(
            category='salary'
        ).count()
        
        self.assertEqual(salary_count, 1)
    
    def test_net_balance(self):
        """Test calculating net balance"""
        from django.db.models import Sum
        
        income = FinancialRecords.objects.filter(
            type_of_record='income'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        expense = FinancialRecords.objects.filter(
            type_of_record='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        net_balance = income - expense
        self.assertEqual(net_balance, Decimal('145000.00'))


class TestRoleBasedValidation(TestCase):
    """Test role-based data validation"""
    
    def test_admin_role(self):
        """Test that admin role is valid"""
        user = User.objects.create_user(username='admin', email='admin@example.com')
        profile = UserProfile.objects.create(
            user=user,
            email='admin@example.com',
            user_name='admin',
            password_hash='hash',
            role='admin'
        )
        self.assertEqual(profile.role, 'admin')
    
    def test_analyst_role(self):
        """Test that analyst role is valid"""
        user = User.objects.create_user(username='analyst', email='analyst@example.com')
        profile = UserProfile.objects.create(
            user=user,
            email='analyst@example.com',
            user_name='analyst',
            password_hash='hash',
            role='analyst'
        )
        self.assertEqual(profile.role, 'analyst')
    
    def test_viewer_role(self):
        """Test that viewer role is valid"""
        user = User.objects.create_user(username='viewer', email='viewer@example.com')
        profile = UserProfile.objects.create(
            user=user,
            email='viewer@example.com',
            user_name='viewer',
            password_hash='hash',
            role='viewer'
        )
        self.assertEqual(profile.role, 'viewer')
    
    def test_user_active_status(self):
        """Test user active/inactive status"""
        user = User.objects.create_user(username='active', email='active@example.com')
        active_profile = UserProfile.objects.create(
            user=user,
            email='active@example.com',
            user_name='active',
            password_hash='hash',
            role='admin',
            is_active=True
        )
        self.assertTrue(active_profile.is_active)
        
        user2 = User.objects.create_user(username='inactive', email='inactive@example.com')
        inactive_profile = UserProfile.objects.create(
            user=user2,
            email='inactive@example.com',
            user_name='inactive',
            password_hash='hash',
            role='viewer',
            is_active=False
        )
        self.assertFalse(inactive_profile.is_active)
