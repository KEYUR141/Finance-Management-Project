import os
from django.core.management.base import BaseCommand
from app.models import FinancialRecords, UserProfile     
from decimal import Decimal
import pandas as pd


# ── SET YOUR EXCEL FILE PATH HERE ─────────────────────────────────────────────
EXCEL_FILE_PATH = f'D:\\Django_Python_Practice\\Projects_High\\Finance-Management-Project\\Backend\\project\\finance_seed_v3.xlsx'  
# ──────────────────────────────────────────────────────────────────────────────


class Command(BaseCommand):
    help = "Seed financial records from Excel file"

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
            help=f'Path to Excel seed file (default: {EXCEL_FILE_PATH})',
        )

    def handle(self, *args, **options):
        excel_path = options['path']

        # ── Validate file ──────────────────────────────────────────────
        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(
                f"\n❌ File not found: {excel_path}"
                f"\n   Put the Excel file there or pass --path:"
                f"\n   python manage.py seed_db --path /your/path/finance_seed_v3.xlsx\n"
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
            self.stdout.write(self.style.ERROR(f"❌ Failed to read FinancialRecords sheet: {e}"))
            return

        self.stdout.write(f"\n📊 Found {len(records_df)} records. Processing...\n")

        skipped = 0
        objs = []

        for idx, row in records_df.iterrows():
            email = row["created_by_email"]

            # Find UserProfile by email
            try:
                user_profile = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️  Row {idx + 2}: UserProfile with email '{email}' not found, skipping."
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
        self.stdout.write(self.style.SUCCESS(f"\n✅ Seeded {len(objs)} records."))
        if skipped:
            self.stdout.write(self.style.WARNING(f"   Skipped:              {skipped} rows"))
        self.stdout.write(f"   Active records:       {len(objs) - soft_deleted}")
        self.stdout.write(f"   Soft-deleted records: {soft_deleted}\n")