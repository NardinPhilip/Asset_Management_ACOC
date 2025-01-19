from django.db import models
import random

class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

import uuid
from django.db import models

class Asset(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    asset_serial_number = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    qr_code_identifier = models.CharField(max_length=100, unique=True, blank=True)  # Unique identifier for the QR code

    def save(self, *args, **kwargs):
        if not self.asset_serial_number:
            self.asset_serial_number = self.generate_unique_serial_number()
        if not self.qr_code_identifier:
            self.qr_code_identifier = str(uuid.uuid4())  # Generate a UUID for the QR code
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_unique_serial_number(self):
        """Generate a unique serial number in the format: {branch_code}-{category_code}-{incremental_6_digit_number}."""
        branch_code = self.branch.code
        category_code = self.category.code

        # Get the last asset in the same branch and category
        last_asset = Asset.objects.filter(branch=self.branch, category=self.category).order_by('-asset_serial_number').first()

        if last_asset:
            # Extract the incremental number from the last asset's serial number
            last_incremental_number = int(last_asset.asset_serial_number.split('-')[-1])
            incremental_number = last_incremental_number + 1
        else:
            # If no assets exist for this branch and category, start from 100000
            incremental_number = 100000

        # Ensure the incremental number is 6 digits
        incremental_number = f"{incremental_number:06d}"

        # Return the combined serial number
        return f"{branch_code}-{category_code}-{incremental_number}"

    def generate_qr_code(self):
        """Generate and save the QR code."""
        import qrcode
        from io import BytesIO
        from django.core.files import File

        qr_data = self.qr_code_identifier  # Use the qr_code_identifier as the QR code data
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate the image and save it as a file
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)
        self.qr_code.save(f"{self.qr_code_identifier}.png", File(buffer), save=False)
        
from django.db import models
from django.utils import timezone

class AuditSession(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    scanned_assets = models.ManyToManyField(Asset, related_name='audit_sessions')

    def __str__(self):
        return f"Audit Session {self.id} - {self.start_time}"