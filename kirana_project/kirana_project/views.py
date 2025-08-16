from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, F
from sales.models import Sale
from customers.models import Customer, CustomerCredit
from products.models import Product
from suppliers.models import Expense

def dashboard(request):
    today = timezone.now().date()
    
    # Today's statistics
    today_sales = Sale.objects.filter(date__date=today).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    # Pending credit
    pending_credit = CustomerCredit.objects.aggregate(
        total=Sum('total_credit')
    )['total'] or 0
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        stock__lte=F('min_stock_level'),
        is_active=True
    )[:5]
    
    # Recent sales
    recent_sales = Sale.objects.filter(date__date=today).order_by('-date')[:10]
    
    # High credit customers
    high_credit_customers = Customer.objects.filter(
        credit__total_credit__gt=1000
    ).order_by('-credit__total_credit')[:5]
    
    context = {
        'today': today,
        'today_sales': today_sales['total'] or 0,
        'today_transactions': today_sales['count'] or 0,
        'pending_credit': pending_credit,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'high_credit_customers': high_credit_customers,
    }
    
    return render(request, 'dashboard.html', context)
