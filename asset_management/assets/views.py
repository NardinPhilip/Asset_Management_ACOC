from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User
from io import BytesIO
import json
import qrcode
import uuid  # Add this import
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .models import Branch, Category, Asset, AuditSession
from reportlab.pdfgen import canvas

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'index')  # Redirect to 'index' or the next URL
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')  # Use messages framework
    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
        else:
            # Create the user
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')  # Redirect to the login page after successful registration

    return render(request, 'register.html')


@login_required
def index(request):
    # Fetch all branches and categories (including deleted ones for stats)
    all_branches = Branch.objects.all()
    all_categories = Category.objects.all()

    # Fetch non-deleted branches and categories for dropdowns
    branches = Branch.objects.filter(is_deleted=False)
    categories = Category.objects.filter(is_deleted=False)

    # Handling search query and filters
    search_query = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_filter', '')
    category_filter = request.GET.get('category_filter', '')

    assets = Asset.objects.all()

    # Apply search filter for asset_serial_number or description
    if search_query:
        assets = assets.filter(asset_serial_number__icontains=search_query) | assets.filter(description__icontains=search_query)

    # Apply branch filter
    if branch_filter:
        assets = assets.filter(branch__id=branch_filter)

    # Apply category filter
    if category_filter:
        assets = assets.filter(category__id=category_filter)

    # Check if 'value' field exists in Asset model
    value_exists = hasattr(Asset, 'value')

    # Calculate summary statistics
    total_assets = assets.count()
    total_value = assets.aggregate(total_value=Sum('value'))['total_value'] if value_exists else 0
    total_in_branch = assets.filter(branch__id=branch_filter).count() if branch_filter else 0
    total_in_category = assets.filter(category__id=category_filter).count() if category_filter else 0
    total_branches = all_branches.filter(is_deleted=False).count()  # Only non-deleted branches
    total_categories = all_categories.filter(is_deleted=False).count()  # Only non-deleted categories

    context = {
        'branches': branches,  # Non-deleted branches for dropdown
        'categories': categories,  # Non-deleted categories for dropdown
        'assets': assets,
        'total_assets': total_assets,
        'total_value': total_value,
        'total_in_branch': total_in_branch,
        'total_in_category': total_in_category,
        'total_branches': total_branches,
        'total_categories': total_categories,
        'search_query': search_query,
        'branch_filter': branch_filter,
        'category_filter': category_filter,
        'value_exists': value_exists
    }

    return render(request, 'index.html', context)

@login_required
def add_branch(request, branch_id=None):
    branch = None
    if branch_id:
        # Fetch the branch for editing
        branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        if not name or not code:
            messages.error(request, 'Both name and code are required.')
        else:
            if branch:
                # Editing an existing branch
                if Branch.objects.filter(code=code, is_deleted=False).exclude(id=branch.id).exists():
                    messages.error(request, 'A Branch with this code already exists.')
                else:
                    branch.name = name
                    branch.code = code
                    branch.save()
                    messages.success(request, 'Branch updated successfully!')
                    return redirect('add_branch')
            else:
                # Adding a new branch
                if Branch.objects.filter(code=code, is_deleted=False).exists():
                    messages.error(request, 'A branch with this code already exists.')
                else:
                    Branch.objects.create(name=name, code=code)
                    messages.success(request, 'Branch added successfully!')
                    return redirect('add_branch')

    # Fetch active and soft-deleted branches
    branches = Branch.objects.filter(is_deleted=False)  # Active branches
    deleted_branches = Branch.objects.filter(is_deleted=True)  # Soft-deleted branches

    return render(request, 'add_branch.html', {
        'branches': branches,
        'deleted_branches': deleted_branches,  # Corrected variable name
        'branch': branch,  # Pass the branch being edited (if any)
    })

@login_required
def add_category(request, category_id=None):
    category = None
    if category_id:
        # Fetch the category for editing
        category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        if not name or not code:
            messages.error(request, 'Both name and code are required.')
        else:
            if category:
                # Editing an existing category
                if Category.objects.filter(code=code, is_deleted=False).exclude(id=category.id).exists():
                    messages.error(request, 'A category with this code already exists.')
                else:
                    category.name = name
                    category.code = code
                    category.save()
                    messages.success(request, 'Category updated successfully!')
                    return redirect('add_category')
            else:
                # Adding a new category
                if Category.objects.filter(code=code, is_deleted=False).exists():
                    messages.error(request, 'A category with this code already exists.')
                else:
                    Category.objects.create(name=name, code=code)
                    messages.success(request, 'Category added successfully!')
                    return redirect('add_category')

    # Fetch active and soft-deleted categories
    categories = Category.objects.filter(is_deleted=False)  # Active categories
    deleted_categories = Category.objects.filter(is_deleted=True)  # Soft-deleted categories

    return render(request, 'add_category.html', {
        'categories': categories,
        'deleted_categories': deleted_categories,
        'category': category,  # Pass the category being edited (if any)
    })

# Review Category View
@login_required
def review_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'review_category.html', {'category': category})

# Edit Category View
@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if not name or not code:
            messages.error(request, 'Both name and code are required.')
        else:
            category.name = name
            category.code = code
            category.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('add_category')
    return render(request, 'edit_category.html', {'category': category})

# Delete Category View
@csrf_exempt
@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        try:
            category = get_object_or_404(Category, id=category_id)
            category.is_deleted = True  # Soft delete
            category.save()
            return JsonResponse({'success': True})
        except Exception as e:
            # Log the error for debugging
            print(f"Error deleting category: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

# Category List View
@login_required
def category_list(request):
    categories = Category.objects.filter(is_deleted=False)  # Only fetch non-deleted categories
    return render(request, 'category_list.html', {'categories': categories})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Branch

@login_required
def edit_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if not name or not code:
            messages.error(request, 'Both name and code are required.')
        else:
            branch.name = name
            branch.code = code
            branch.save()
            messages.success(request, 'Branch updated successfully!')
            return redirect('add_branch')
    return render(request, 'edit_branch.html', {'branch': branch})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Branch


@csrf_exempt
@login_required
def delete_branch(request, branch_id):
    if request.method == 'POST':
        try:
            branch = get_object_or_404(Branch, id=branch_id)
            branch.is_deleted = True  # Soft delete
            branch.save()
            return JsonResponse({'success': True})
        except Exception as e:
            # Log the error for debugging
            print(f"Error deleting category: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)



@login_required
def branch_list(request):
    branches = Branch.objects.filter(is_deleted=False)
    return render(request, 'branch_list.html', {'branches': branches})

# Asset Management View
@login_required
def asset_management(request):
    branches = Branch.objects.filter(is_deleted=False)
    categories = Category.objects.filter(is_deleted=False)
    assets = Asset.objects.all()
    return render(request, 'asset_management.html', {'branches': branches, 'categories': categories, 'assets': assets})

from django.template.loader import render_to_string

import random  # Import the random module for generating random numbers

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
import qrcode
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Branch, Category, Asset

@login_required
def generate_asset(request):
    if request.method == 'POST':
        branch_id = request.POST.get('branch')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')  # Get the uploaded photo

        if not branch_id or not category_id or not description:
            messages.error(request, 'All fields are required.')
        else:
            branch = get_object_or_404(Branch, id=branch_id)
            category = get_object_or_404(Category, id=category_id)

            # Create the asset
            asset = Asset(
                branch=branch,
                category=category,
                description=description,
                photo=photo,
            )

            # Generate a random 6-digit number for the asset number
            asset_number = f"{random.randint(100000, 999999)}"  # Random 6-digit number

            # Generate the serial number using branch code, category code, and the 6-digit asset number
            asset.asset_serial_number = f"{branch.code}-{category.code}-{asset_number}"

            # Generate a unique QR code identifier
            asset.qr_code_identifier = asset.asset_serial_number

            # Save the asset to generate an ID
            asset.save()

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(asset.qr_code_identifier)  # Use the QR code identifier as the data
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save the QR code image to the asset
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"qr_{asset.qr_code_identifier}.png"
            asset.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=True)

            # Generate PDF with only the QR code sticker
            pdf_buffer = BytesIO()
            pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

            # Center the QR code on the PDF page
            qr_code_path = asset.qr_code.path
            qr_width = 200  # Width of the QR code
            qr_height = 200  # Height of the QR code
            page_width, page_height = letter  # Get the dimensions of the PDF page
            x = (page_width - qr_width) / 2  # Center horizontally
            y = (page_height - qr_height) / 2  # Center vertically

            # Draw the QR code
            pdf.drawImage(qr_code_path, x, y, width=qr_width, height=qr_height)

            # Save the PDF
            pdf.showPage()
            pdf.save()

            # Prepare the PDF for download
            pdf_buffer.seek(0)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="sticker_{asset.asset_serial_number}.pdf"'

            # Pass the asset and PDF response to the template
            return render(request, 'generate_asset.html', {
                'branches': Branch.objects.filter(is_deleted=False),
                'categories': Category.objects.filter(is_deleted=False),
                'asset': asset,
                'pdf_response': response,
            })

    branches = Branch.objects.filter(is_deleted=False)
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'generate_asset.html', {'branches': branches, 'categories': categories})

@login_required
def generate_report(request):
    branches = Branch.objects.filter(is_deleted=False)
    categories = Category.objects.filter(is_deleted=False)
    assets = Asset.objects.all()

    # Apply filters
    branch_filter = request.GET.get('branch')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')

    if branch_filter:
        assets = assets.filter(branch__name__icontains=branch_filter)
    if category_filter:
        assets = assets.filter(category__code__icontains=category_filter)
    if search_query:
        assets = assets.filter(description__icontains=search_query)

    context = {
        'branches': branches,
        'categories': categories,
        'assets': assets,
    }
    return render(request, 'generate_report.html', context)

@login_required
def start_audit(request):
    # Create a new audit session
    audit_session = AuditSession.objects.create()
    request.session['audit_session_id'] = audit_session.id
    return render(request, 'start_audit.html', {'audit_session': audit_session})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def scan_qr_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        qr_code_identifier = data.get('qr_code')  # This should be the qr_code_identifier

        try:
            # Look up the asset by the qr_code_identifier
            asset = Asset.objects.get(qr_code_identifier=qr_code_identifier)

            # Add the asset to the current audit session
            audit_session_id = request.session.get('audit_session_id')
            if audit_session_id:
                audit_session = AuditSession.objects.get(id=audit_session_id)
                audit_session.scanned_assets.add(asset)
                audit_session.save()

            response_data = {
                'status': 'success',
                'asset': {
                    'description': asset.description,
                    'asset_serial_number': asset.asset_serial_number,
                    'branch_name': asset.branch.name,
                    'category_name': asset.category.name
                }
            }
            return JsonResponse(response_data)
        except Asset.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Asset not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

from reportlab.platypus import Image  # Import the Image class
from reportlab.lib.utils import ImageReader  # Import ImageReader for better image handling

@login_required
def end_audit(request):
    audit_session_id = request.session.get('audit_session_id')
    if not audit_session_id:
        return HttpResponse("No active audit session.")
    
    try:
        audit_session = AuditSession.objects.get(id=audit_session_id)
    except AuditSession.DoesNotExist:
        return HttpResponse("Invalid audit session.")
    
    audit_session.end_time = timezone.now()
    audit_session.save()
    
    scanned_assets = audit_session.scanned_assets.all()
    all_assets = Asset.objects.all()
    not_scanned_assets = all_assets.exclude(id__in=scanned_assets.values_list('id', flat=True))

    # Generate PDF report
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="audit_report.pdf"'
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Asset Audit Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Audit Session ID: {audit_session.id}", styles['BodyText']))
    elements.append(Paragraph(f"Start Time: {audit_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['BodyText']))
    elements.append(Paragraph(f"End Time: {audit_session.end_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['BodyText']))
    elements.append(Spacer(1, 24))

    # Scanned Assets Section
    elements.append(Paragraph("Scanned Assets", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Include asset photos in the scanned assets table
    scanned_data = [["Description", "Serial Number", "Branch", "Category", "Photo"]]
    for asset in scanned_assets:
        # Check if the asset has a photo
        if asset.photo:
            try:
                # Use ImageReader to handle the image file
                photo = Image(asset.photo.path, width=50, height=50)
            except Exception as e:
                print(f"Error loading image: {e}")  # Debugging
                photo = "No Photo"
        else:
            photo = "No Photo"
        
        scanned_data.append([
            asset.description or 'N/A',
            asset.asset_serial_number,
            asset.branch.name,
            asset.category.name,
            photo
        ])
    
    scanned_table = Table(scanned_data)
    scanned_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(scanned_table)
    elements.append(Spacer(1, 24))

    # Missing Assets Section
    elements.append(Paragraph("Missing Assets", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Include asset description in the missing assets table
    missing_data = [["Serial Number", "Description", "Branch", "Category"]]
    for asset in not_scanned_assets:
        missing_data.append([
            asset.asset_serial_number,
            asset.description or 'N/A',
            asset.branch.name,
            asset.category.name
        ])
    
    missing_table = Table(missing_data)
    missing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(missing_table)

    # Build the PDF
    pdf.build(elements)
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    
    # Clear the audit session from the session
    del request.session['audit_session_id']
    
    return response


@csrf_exempt  # Temporarily disable CSRF for testing (remove in production)
@login_required
def restore_branch(request, branch_id):
    if request.method == 'POST':
        try:
            # Fetch the branch by ID
            branch = get_object_or_404(Branch, id=branch_id)
            
            # Check if a non-deleted branch with the same code already exists
            if Branch.objects.filter(code=branch.code, is_deleted=False).exists():
                return JsonResponse({'success': False, 'error': 'A branch with this code already exists.'})
            
            # Restore the branch by setting is_deleted to False
            branch.is_deleted = False
            branch.save()
            
            # Return a JSON response for AJAX requests
            return JsonResponse({'success': True})
        except Exception as e:
            # Log the error for debugging
            print(f"Error restoring branch: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

@csrf_exempt
@login_required
def restore_category(request, category_id):
    if request.method == 'POST':
        try:
            # Fetch the category by ID
            category = get_object_or_404(Category, id=category_id)
            
            # Check if a non-deleted category with the same code already exists
            if Category.objects.filter(code=category.code, is_deleted=False).exists():
                return JsonResponse({'success': False, 'error': 'A category with this code already exists.'})
            
            # Restore the category by setting is_deleted to False
            category.is_deleted = False
            category.save()
            
            # Return a JSON response for AJAX requests
            return JsonResponse({'success': True})
        except Exception as e:
            # Log the error for debugging
            print(f"Error restoring category: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)