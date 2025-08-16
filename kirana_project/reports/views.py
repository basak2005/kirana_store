from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from sales.models import Sale
from customers.models import Customer
from products.models import Product
from suppliers.models import Supplier

# Create your views here.
def reports_dashboard(request):
    # Get today's data
    today = datetime.now().date()
    
    # Basic statistics
    total_sales_today = Sale.objects.filter(date__date=today).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=5).count()
    
    context = {
        'total_sales_today': total_sales_today,
        'total_customers': total_customers,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'reports/dashboard.html', context)

def daily_report(request):
    today = datetime.now().date()
    
    # Daily sales data
    daily_sales = Sale.objects.filter(date__date=today).aggregate(
        total_amount=Sum('total_amount'),
        total_sales=Count('id')
    )
    
    recent_sales = Sale.objects.filter(date__date=today).order_by('-date')[:10]
    
    context = {
        'date': today,
        'total_amount': daily_sales['total_amount'] or 0,
        'total_sales': daily_sales['total_sales'] or 0,
        'recent_sales': recent_sales,
    }
    return render(request, 'reports/daily_report.html', context)

def monthly_report(request):
    # Current month data
    today = datetime.now().date()
    first_day = today.replace(day=1)
    
    monthly_sales = Sale.objects.filter(date__date__gte=first_day).aggregate(
        total_amount=Sum('total_amount'),
        total_sales=Count('id')
    )
    
    context = {
        'month': today.strftime('%B %Y'),
        'total_amount': monthly_sales['total_amount'] or 0,
        'total_sales': monthly_sales['total_sales'] or 0,
    }
    return render(request, 'reports/monthly_report.html', context)

def sales_analysis(request):
    # Sales analysis data
    total_sales = Sale.objects.aggregate(
        total_amount=Sum('total_amount'),
        total_count=Count('id')
    )
    
    context = {
        'total_amount': total_sales['total_amount'] or 0,
        'total_count': total_sales['total_count'] or 0,
    }
    return render(request, 'reports/sales_analysis.html', context)

def profit_loss(request):
    return render(request, 'reports/profit_loss.html')

def gst_report(request):
    return render(request, 'reports/gst_report.html')
