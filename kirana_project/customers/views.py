from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import Customer, CustomerCredit

def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'customers/customer_list.html', {'customers': customers})

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
    # Ensure all customers have a CustomerCredit record
    from .models import CustomerCredit
    for customer in Customer.objects.all():
        CustomerCredit.objects.get_or_create(customer=customer)

    customers_with_credit = Customer.objects.filter(
        credit__total_credit__gt=0
    ).order_by('-credit__total_credit')

    total_credit = CustomerCredit.objects.aggregate(
        total=Sum('total_credit')
    )['total'] or 0

    context = {
        'customers_with_credit': customers_with_credit,
        'total_credit': total_credit,
    }
    return render(request, 'customers/credit_report.html', context)
