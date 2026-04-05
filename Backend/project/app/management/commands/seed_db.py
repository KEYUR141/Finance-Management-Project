import os
import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import FinancialRecords, UserProfile     
from decimal import Decimal
import pandas as pd


# ── DETERMINE EXCEL FILE PATH ─────────────────────────────────────────────
# Try multiple locations for the Excel file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # Project root
EXCEL_FILE_PATH = None

# List of possible paths to check
possible_paths = [
    os.path.join(BASE_DIR, 'finance_seed_v3.xlsx'),  # Root of project
    'finance_seed_v3.xlsx',  # Current directory
    '/app/finance_seed_v3.xlsx',  # Docker /app
]

for path in possible_paths:
    if os.path.exists(path):
        EXCEL_FILE_PATH = path
        break
# ──────────────────────────────────────────────────────────────────────────


DEMO_USERS = [
    ("Demo_admin", "demo.admin@gmail.com", "admin", "demo@admin2026"),
    ("Demo_analyst", "demo.analyst@gmail.com", "analyst", "demo@analyst2026"),
    ("Demo_viewer", "demo.viewer@gmail.com", "viewer", "demo@viewer2026"),
]


class Command(BaseCommand):
    help = "Seed financial records from Excel file (optional)"

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def seed_demo_users(self):
        created_count = 0
        updated_count = 0

        for user_name, email, role, plain_password in DEMO_USERS:
            django_user, user_created = User.objects.get_or_create(
                username=user_name,
                defaults={
                    "email": email,
                    "is_active": True,
                },
            )

            if not user_created:
                user_changed = False
                if django_user.email != email:
                    django_user.email = email
                    user_changed = True
                if not django_user.is_active:
                    django_user.is_active = True
                    user_changed = True
                if user_changed:
                    django_user.save()

            password_hash = self.hash_password(plain_password)
            profile, profile_created = UserProfile.objects.get_or_create(
                email=email,
                defaults={
                    "user_name": user_name,
                    "user": django_user,
                    "role": role,
                    "is_active": True,
                    "password_hash": password_hash,
                },
            )

            if profile_created:
                created_count += 1
            else:
                profile_changed = False
                if profile.user_name != user_name:
                    profile.user_name = user_name
                    profile_changed = True
                if profile.user_id != django_user.id:
                    profile.user = django_user
                    profile_changed = True
                if profile.role != role:
                    profile.role = role
                    profile_changed = True
                if not profile.is_active:
                    profile.is_active = True
                    profile_changed = True
                if profile.password_hash != password_hash:
                    profile.password_hash = password_hash
                    profile_changed = True
                if profile_changed:
                    profile.save()
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Demo users ready. Created: {created_count}, Updated: {updated_count}"
        ))

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing financial records before seeding',
        )
        parser.add_argument(
            '--path',
            type=str,
            default=EXCEL_FILE_PATH,
            help=f'Path to Excel seed file',
        )

    def handle(self, *args, **options):
        excel_path = options['path']

        # Ensure demo Django User + UserProfile records exist before data seeding
        self.seed_demo_users()

        # ── Validate file - if not found, warn but don't crash ──────────────────────────
        if not excel_path or not os.path.exists(excel_path):
            self.stdout.write(self.style.WARNING(
                f"\n  Excel seed file not found. Skipping data seeding."
                f"\n   (This is OK in production if you don't have the Excel file)"
                f"\n   If needed, pass --path to specify a custom location.\n"
            ))
            return

        self.stdout.write(f"\n📂 Reading: {excel_path}\n")

        # ── Flush if requested ─────────────────────────────────────────
        if options['flush']:
            FinancialRecords.objects.all().delete()
            self.stdout.write(self.style.WARNING("🗑️  Flushed existing financial records.\n"))

        # ── Read FinancialRecords sheet ────────────────────────────────
        try:
            records_df = pd.read_excel(excel_path, sheet_name="FinancialRecords")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f" Failed to read FinancialRecords sheet: {e}"))
            return

        self.stdout.write(f"\n Found {len(records_df)} records. Processing...\n")

        skipped = 0
        objs = []

        for idx, row in records_df.iterrows():
            email = row["created_by_email"]

            # Find UserProfile by email
            try:
                user_profile = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"    Row {idx + 2}: UserProfile with email '{email}' not found, skipping."
                ))
                skipped += 1
                continue

            objs.append(FinancialRecords(
                created_by=user_profile,
                amount=Decimal(str(row["amount"])),
                type_of_record=str(row["type_of_record"]).strip(),
                category=str(row["category"]).strip(),
                date=pd.to_datetime(row["date"]).date(),
                notes=str(row["notes"]) if pd.notna(row["notes"]) else "",
                is_deleted=bool(row["is_deleted"]),
            ))

        FinancialRecords.objects.bulk_create(objs)

        soft_deleted = sum(1 for o in objs if o.is_deleted)
        self.stdout.write(self.style.SUCCESS(f"\nSeeded {len(objs)} records."))
        if skipped:
            self.stdout.write(self.style.WARNING(f"   Skipped:              {skipped} rows"))
        self.stdout.write(f"   Active records:       {len(objs) - soft_deleted}")
        self.stdout.write(f"   Soft-deleted records: {soft_deleted}\n")