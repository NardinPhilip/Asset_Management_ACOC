from django.shortcuts import render
from .models import Branch, Category, Asset
from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from .models import Branch, Category, Asset
from django.template.loader import render_to_string
from xhtml2pdf import pisa

# View to display the main asset management page with search and filters
def index(request):
    branches = Branch.objects.all()
    categories = Category.objects.all()

    # Handling search query
    search_query = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_filter', '')
    category_filter = request.GET.get('category_filter', '')

    assets = Asset.objects.all()

    # Apply search filter for serial_number or description
    if search_query:
        assets = assets.filter(serial_number__icontains=search_query) | assets.filter(description__icontains=search_query)

    # Apply branch filter
    if branch_filter:
        assets = assets.filter(branch__id=branch_filter)

    # Apply category filter
    if category_filter:
        assets = assets.filter(category__id=category_filter)

    # Check if 'value' field exists in Asset model
    try:
        Asset._meta.get_field('value')
        value_exists = True
    except Exception:
        value_exists = False

    # Calculate summary statistics
    total_assets = assets.count()
    total_value = assets.aggregate(total_value=Sum('value'))['total_value'] if value_exists else 0
    total_in_branch = assets.filter(branch__id=branch_filter).count() if branch_filter else 0
    total_in_category = assets.filter(category__id=category_filter).count() if category_filter else 0
    total_branches = branches.count()
    total_categories = categories.count()

    context = {
        'branches': branches,
        'categories': categories,
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

# View to add a new branch
def add_branch(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        Branch.objects.create(name=name, code=code)
        return redirect('add_branch')
    branches = Branch.objects.all()  # Fetch all branches
    return render(request, 'add_branch.html', {'branches': branches})

# View to add a new category
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        Category.objects.create(name=name, code=code)
    return render(request, 'add_category.html')

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render
from .models import Branch, Category, Asset
from django.shortcuts import render
from django.db.models import Max
from django.db import transaction
from .models import Branch, Category, Asset
from django.shortcuts import render, redirect
from .models import Branch, Category, Asset

from django.shortcuts import render
from .models import Branch, Category, Asset



# View to display asset management (assets, branches, categories)
def asset_management(request):
    branches = Branch.objects.all()
    categories = Category.objects.all()
    assets = Asset.objects.all()
    return render(request, 'asset_management.html', {'branches': branches, 'categories': categories, 'assets': assets})

# View to display all branches
def view_branches(request):
    branches = Branch.objects.all()
    return render(request, 'view_branches.html', {'branches': branches})

# View to display all categories
def view_categories(request):
    categories = Category.objects.all()
    return render(request, 'view_categories.html', {'categories': categories})

# View to display all assets
def view_assets(request):
    assets = Asset.objects.all()
    return render(request, 'view_assets.html', {'assets': assets})

from django.shortcuts import render, redirect
from .models import Branch, Category, Asset
from django.shortcuts import render
from .models import Branch, Category, Asset

from django.shortcuts import render
from .models import Branch, Category, Asset

def generate_asset(request):
    if request.method == 'POST':
        branch_id = request.POST.get('branch')
        category_id = request.POST.get('category')
        description = request.POST.get('description')

        # Get the Branch and Category objects using the IDs
        branch = Branch.objects.get(id=branch_id)
        category = Category.objects.get(id=category_id)

        # Create the Asset instance with the ForeignKey relationships
        asset = Asset.objects.create(
            branch=branch,
            category=category,
            description=description,
        )

        # The serial number is generated automatically when saving
        asset.save()

        # Render the asset creation page with the newly created asset
        return render(request, 'generate_asset.html', {'asset': asset})

    # If it's a GET request, pass the branches and categories to the template
    branches = Branch.objects.all()
    categories = Category.objects.all()

    return render(request, 'generate_asset.html', {'branches': branches, 'categories': categories})


def generate_report(request):
    # Fetch all branches and categories for the filters
    branches = Branch.objects.all()
    categories = Category.objects.all()
    
    # Fetch all assets for the table (filtered if filters are applied)
    assets = Asset.objects.all()
    branch_filter = request.GET.get('branch')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')

    # Apply branch filter if selected
    if branch_filter:
        assets = assets.filter(branch__name__icontains=branch_filter)
    
    # Apply category filter if selected
    if category_filter:
        assets = assets.filter(category__code__icontains=category_filter)
    
    # Apply search query if provided
    if search_query:
        assets = assets.filter(
            description__icontains=search_query
        )

    context = {
        'branches': branches,
        'categories': categories,
        'assets': assets,
    }
    return render(request, 'generate_report.html', context)


from django.shortcuts import render
from .models import Branch, Category, Asset


from django.shortcuts import render, redirect
from .models import AuditSession

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

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Asset
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.http import HttpResponse
from .models import Asset


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import AuditSession, Asset
from django.utils import timezone  # Add this import
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from django.utils import timezone
from .models import AuditSession, Asset


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from django.utils import timezone
from .models import AuditSession, Asset

def end_audit(request):
    audit_session_id = request.session.get('audit_session_id')
    if not audit_session_id:
        return HttpResponse("No active audit session.")

    audit_session = AuditSession.objects.get(id=audit_session_id)
    audit_session.end_time = timezone.now()
    audit_session.save()

    # Retrieve scanned assets
    scanned_assets = audit_session.scanned_assets.all()
    all_assets = Asset.objects.all()
    not_scanned_assets = all_assets.exclude(id__in=scanned_assets.values_list('id', flat=True))

    # Prepare the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="audit_report.pdf"'

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the PDF content
    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Asset Audit Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Add audit session details
    elements.append(Paragraph(f"Audit Session ID: {audit_session.id}", styles['BodyText']))
    elements.append(Paragraph(f"Start Time: {audit_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['BodyText']))
    elements.append(Paragraph(f"End Time: {audit_session.end_time.strftime('%Y-%m-%d %H:%M:%S')}", styles['BodyText']))
    elements.append(Spacer(1, 24))

    # Add a title for scanned assets
    elements.append(Paragraph("Scanned Assets", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Create a table for scanned assets
    scanned_data = [["Description", "Serial Number", "Branch", "Category"]]
    for asset in scanned_assets:
        scanned_data.append([
            asset.description or 'N/A',
            asset.asset_serial_number,
            asset.branch.name,
            asset.category.name
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

    # Add a title for missing assets
    elements.append(Paragraph("Missing Assets", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Create a table for missing assets
    missing_data = [["Serial Number", "Branch", "Category"]]
    for asset in not_scanned_assets:
        missing_data.append([
            asset.asset_serial_number,
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

    # Finalize PDF
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()

    # Clear session data
    del request.session['audit_session_id']

    return response
from django.shortcuts import render, get_object_or_404, redirect
from .models import Branch

def edit_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        # Update the branch with new data
        branch.name = request.POST.get('name')
        branch.code = request.POST.get('code')
        branch.save()
        return redirect('add_branch')
    return render(request, 'edit_branch.html', {'branch': branch})

def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    branch.delete()
    return redirect('add_branch')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        # Update only the name and code fields
        category.name = request.POST.get('name')
        category.code = request.POST.get('code')
        category.save()
        return redirect('add_category')
    return render(request, 'edit_category.html', {'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('add_category')