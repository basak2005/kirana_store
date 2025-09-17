from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import Customer, CustomerCredit
from sales.models import Sale
from decimal import Decimal

def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    
    # Calculate outstanding credit for each customer
    for customer in customers:
        total_credit_sales = Sale.objects.filter(
            customer=customer, 
            is_credit=True
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        total_paid = Sale.objects.filter(
            customer=customer, 
            is_credit=True, 
            credit_paid=True
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        outstanding_credit = total_credit_sales - total_paid
        
        # Update or create CustomerCredit record
        credit_record, created = CustomerCredit.objects.get_or_create(customer=customer)
        credit_record.total_credit = outstanding_credit
        credit_record.save()
    
    # Calculate total outstanding credit for dashboard
    total_outstanding = CustomerCredit.objects.aggregate(
        total=Sum('total_credit')
    )['total'] or Decimal('0.00')
    
    context = {
        'customers': customers,
        'total_outstanding_credit': total_outstanding
    }
    return render(request, 'customers/customer_list.html', context)

def add_customer(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            address = request.POST.get('address')
            
            # Create and save customer
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                address=address
            )
            # Ensure CustomerCredit exists for every customer
            from .models import CustomerCredit
            CustomerCredit.objects.get_or_create(customer=customer)
            
            messages.success(request, f'Customer "{name}" added successfully!')
            return redirect('customers:customer_list')
        except Exception as e:
            messages.error(request, f'Error adding customer: {str(e)}')
    return render(request, 'customers/customer_form.html')

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/customer_detail.html', {'customer': customer})

def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        try:
            # Get form data
            customer.name = request.POST.get('name')
            customer.phone = request.POST.get('phone')
            customer.email = request.POST.get('email')
            customer.address = request.POST.get('address')
            customer.save()
            
            messages.success(request, f'Customer "{customer.name}" updated successfully!')
            return redirect('customers:customer_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error updating customer: {str(e)}')
    return render(request, 'customers/customer_form.html', {'customer': customer})

def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        try:
            customer_name = customer.name  # Store name before deletion
            customer.delete()
            messages.success(request, f'Customer "{customer_name}" deleted successfully!')
            return redirect('customers:customer_list')
        except Exception as e:
            messages.error(request, f'Error deleting customer: {str(e)}')
            return redirect('customers:customer_detail', pk=pk)
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})

def credit_report(request):
    from sales.models import Sale
    from django.db.models import Sum, Q, Count
    
    # Get customers with unpaid credit sales
    customers_with_credit = Customer.objects.filter(
        sale__is_credit=True,
        sale__credit_paid=False
    ).annotate(
        outstanding_credit=Sum('sale__total_amount', filter=Q(sale__is_credit=True, sale__credit_paid=False)),
        unpaid_sales_count=Count('sale', filter=Q(sale__is_credit=True, sale__credit_paid=False))
    ).order_by('-outstanding_credit').distinct()

    # Add unpaid sales to each customer
    for customer in customers_with_credit:
        customer.unpaid_sales = Sale.objects.filter(
            customer=customer,
            is_credit=True,
            credit_paid=False
        )

    # Calculate total outstanding credit
    total_credit = Sale.objects.filter(
        is_credit=True, 
        credit_paid=False
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'customers_with_credit': customers_with_credit,
        'total_credit': total_credit,
    }
    return render(request, 'customers/credit_report.html', context)
