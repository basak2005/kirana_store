from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, ProductCategory

# Create your views here.
def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'products/product_list.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            brand = request.POST.get('brand')
            barcode = request.POST.get('barcode')
            price = request.POST.get('price')
            cost_price = request.POST.get('cost_price')
            gst_rate = request.POST.get('gst_rate') or 0
            stock = request.POST.get('stock') or 0
            min_stock_level = request.POST.get('min_stock_level') or 5
            unit = request.POST.get('unit') or 'pcs'
            category_id = request.POST.get('category')
            category = ProductCategory.objects.get(pk=category_id) if category_id else None

            # Create and save product
            product = Product.objects.create(
                name=name,
                brand=brand,
                barcode=barcode,
                price=float(price),
                cost_price=float(cost_price) if cost_price else 0,
                gst_rate=float(gst_rate),
                stock=int(stock),
                min_stock_level=int(min_stock_level),
                unit=unit,
                category=category
            )
            
            messages.success(request, f'Product "{name}" added successfully!')
            return redirect('products:product_list')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    categories = ProductCategory.objects.all()
    if not categories.exists():
        default_categories = [
            "Groceries", "Beverages", "Snacks", "Personal Care", "Household"
        ]
        for cat_name in default_categories:
            ProductCategory.objects.create(name=cat_name)
        categories = ProductCategory.objects.all()
    return render(request, 'products/product_form.html', {'categories': categories})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = ProductCategory.objects.all()
    if not categories.exists():
        default_categories = [
            "Groceries", "Beverages", "Snacks", "Personal Care", "Household"
        ]
        for cat_name in default_categories:
            ProductCategory.objects.create(name=cat_name)
        categories = ProductCategory.objects.all()
    if request.method == 'POST':
        try:
            # Get form data
            product.name = request.POST.get('name')
            product.brand = request.POST.get('brand')
            product.barcode = request.POST.get('barcode')
            product.price = float(request.POST.get('price'))
            product.cost_price = float(request.POST.get('cost_price')) if request.POST.get('cost_price') else 0
            product.gst_rate = float(request.POST.get('gst_rate')) if request.POST.get('gst_rate') else 0
            product.stock = int(request.POST.get('stock')) if request.POST.get('stock') else 0
            product.min_stock_level = int(request.POST.get('min_stock_level')) if request.POST.get('min_stock_level') else 5
            product.unit = request.POST.get('unit') or 'pcs'
            category_id = request.POST.get('category')
            product.category = ProductCategory.objects.get(pk=category_id) if category_id else None
            product.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products:product_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    return render(request, 'products/product_form.html', {'product': product, 'categories': categories})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product_name = product.name
            product.delete()
            messages.success(request, f'Product "{product_name}" deleted successfully!')
            return redirect('products:product_list')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('products:product_detail', pk=pk)
    return render(request, 'products/product_confirm_delete.html', {'product': product})

def stock_report(request):
    from .models import Product
    from django.db.models import F
    products = Product.objects.all()
    for p in products:
        p.stock_value = p.stock * p.cost_price
        print(f"DEBUG: {p.name} stock={p.stock} cost_price={p.cost_price} stock_value={p.stock_value}")
    out_of_stock = products.filter(stock=0).count()
    low_stock = products.filter(stock__gt=0, stock__lte=F('min_stock_level')).count()
    good_stock = products.filter(stock__gt=F('min_stock_level')).count()
    total_inventory_value = sum([p.stock * p.cost_price for p in products])
    context = {
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'good_stock': good_stock,
        'products': products,
        'total_inventory_value': total_inventory_value,
    }
    return render(request, 'products/stock_report.html', context)

def category_list(request):
    return render(request, 'products/category_list.html')
