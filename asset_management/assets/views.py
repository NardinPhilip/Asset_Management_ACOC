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
    return render(request, 'add_branch.html')

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

def report_view(request):
    branches = Branch.objects.all()
    categories = Category.objects.all()
    assets = Asset.objects.all()

    # You can add filtering logic here if needed based on the request parameters.

    context = {
        'branches': branches,
        'categories': categories,
        'assets': assets,
    }
    return render(request, 'your_template.html', context)


