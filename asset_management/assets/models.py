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

class Asset(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    asset_serial_number = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        if not self.asset_serial_number:
            self.asset_serial_number = self.generate_unique_serial_number()
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_unique_serial_number(self):
        """Generate a unique serial number."""
        # Get the branch code and category code
        branch_code = self.branch.code
        category_code = self.category.code

        # Generate a 6-digit unique ID for the asset within the same branch and category
        asset_id = self.generate_asset_id(branch_code, category_code)

        # Return the combined serial number
        return f"{branch_code}-{category_code}-{asset_id}"

    def generate_asset_id(self, branch_code, category_code):
        """Generate a 6-digit unique ID for the asset."""
        # You can modify the logic here to make sure the IDs are unique within the branch and category
        # For now, we are generating a random 6-digit number.
        asset_id = random.randint(100000, 999999)  # Generate a 6-digit number
        return asset_id

    def generate_qr_code(self):
        """Generate and save the QR code."""
        import qrcode
        from io import BytesIO
        from django.core.files import File

        qr_data = f"Asset Serial Number: {self.asset_serial_number}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate the image and save it as a file
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)
        self.qr_code.save(f"{self.asset_serial_number}.png", File(buffer), save=False)
