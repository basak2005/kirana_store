from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import HttpResponse
from datetime import datetime, timedelta
from calendar import monthrange
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
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

def monthly_report(request):
    # Get current month or specified month
    today = datetime.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # First and last day of the month
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()
    
    # Get daily sales data for the month
    daily_profits = []
    dates = []
    
    current_day = first_day
    while current_day <= last_day:
        daily_sales = Sale.objects.filter(date__date=current_day).aggregate(
            total_revenue=Sum('total_amount')
        )['total_revenue'] or 0
        
        # Calculate profit (assuming 20% profit margin for simplicity)
        # You can modify this based on your actual cost calculation
        daily_profit = float(daily_sales) * 0.20
        
        daily_profits.append(daily_profit)
        dates.append(current_day.day)
        current_day += timedelta(days=1)
    
    # Create bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(dates, daily_profits, color='#28a745', alpha=0.7)
    plt.title(f'Daily Profit Report - {datetime(year, month, 1).strftime("%B %Y")}', fontsize=16, fontweight='bold')
    plt.xlabel('Day of Month', fontsize=12)
    plt.ylabel('Profit (₹)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Format y-axis to show currency
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # Save plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Monthly totals
    monthly_sales = Sale.objects.filter(
        date__date__gte=first_day,
        date__date__lte=last_day
    ).aggregate(
        total_revenue=Sum('total_amount'),
        total_sales=Count('id')
    )
    
    total_profit = float(monthly_sales['total_revenue'] or 0) * 0.20
    
    context = {
        'month': datetime(year, month, 1).strftime('%B %Y'),
        'year': year,
        'month_num': month,
        'total_revenue': monthly_sales['total_revenue'] or 0,
        'total_profit': total_profit,
        'total_sales': monthly_sales['total_sales'] or 0,
        'chart_data': chart_data,
    }
    return render(request, 'reports/monthly_report.html', context)

def yearly_report(request):
    # Get current year or specified year
    today = datetime.now().date()
    year = int(request.GET.get('year', today.year))
    
    # Get monthly profits for the year
    monthly_profits = []
    month_names = []
    
    for month in range(1, 13):
        first_day = datetime(year, month, 1).date()
        last_day = datetime(year, month, monthrange(year, month)[1]).date()
        
        monthly_sales = Sale.objects.filter(
            date__date__gte=first_day,
            date__date__lte=last_day
        ).aggregate(
            total_revenue=Sum('total_amount')
        )['total_revenue'] or 0
        
        # Calculate profit (assuming 20% profit margin)
        monthly_profit = float(monthly_sales) * 0.20
        
        monthly_profits.append(monthly_profit)
        month_names.append(datetime(year, month, 1).strftime('%b'))
    
    # Create bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(month_names, monthly_profits, color='#007bff', alpha=0.7)
    plt.title(f'Monthly Profit Report - {year}', fontsize=16, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Profit (₹)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, profit in zip(bars, monthly_profits):
        if profit > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(monthly_profits)*0.01,
                    f'₹{profit:,.0f}', ha='center', va='bottom', fontsize=9)
    
    # Format y-axis to show currency
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # Save plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Yearly totals
    yearly_sales = Sale.objects.filter(
        date__year=year
    ).aggregate(
        total_revenue=Sum('total_amount'),
        total_sales=Count('id')
    )
    
    total_profit = float(yearly_sales['total_revenue'] or 0) * 0.20
    
    context = {
        'year': year,
        'total_revenue': yearly_sales['total_revenue'] or 0,
        'total_profit': total_profit,
        'total_sales': yearly_sales['total_sales'] or 0,
        'chart_data': chart_data,
    }
    return render(request, 'reports/yearly_report.html', context)

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
