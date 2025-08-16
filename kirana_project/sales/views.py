from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Sale, SaleItem
from customers.models import Customer
from products.models import Product
from decimal import Decimal
import json

# Create your views here.
def sale_list(request):
    sales = Sale.objects.all().order_by('-date')
    return render(request, 'sales/sale_list.html', {'sales': sales})

def new_sale(request):
    if request.method == 'POST':
        try:
            # Get customer
            customer_id = request.POST.get('customer')
            customer = None
            if customer_id:
                customer = Customer.objects.get(pk=customer_id)
            
            payment_mode = request.POST.get('payment_mode', 'cash')
            is_credit = payment_mode == 'credit'
            
            # Create sale
            sale = Sale.objects.create(
                customer=customer,
                payment_mode=payment_mode,
                is_credit=is_credit,
                total_amount=0  # Will be calculated below
            )
            
            # Process items
            products = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')
            prices = request.POST.getlist('price[]')
            
            total_amount = Decimal('0.00')
            subtotal = Decimal('0.00')
            total_gst = Decimal('0.00')
            
            for i, product_id in enumerate(products):
                if product_id and i < len(quantities) and i < len(prices):
                    try:
                        product = Product.objects.get(pk=product_id)
                        quantity = int(quantities[i])
                        unit_price = Decimal(prices[i])
                        # Stock check
                        if product.stock < quantity:
                            messages.error(request, f"{product.name} is out of stock or insufficient stock!")
                            sale.delete()  # Clean up incomplete sale
                            return redirect('sales:new_sale')
                        # Calculate totals
                        line_total = quantity * unit_price
                        gst_amount = line_total * Decimal('0.18')  # 18% GST
                        total_price = line_total + gst_amount
                        # Create sale item
                        from .models import SaleItem
                        SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=quantity,
                            unit_price=unit_price,
                            gst_amount=gst_amount,
                            total_price=total_price
                        )
                        # Update product stock
                        product.stock -= quantity
                        product.save()
                        subtotal += line_total
                        total_gst += gst_amount
                        total_amount += total_price
                    except (Product.DoesNotExist, ValueError) as e:
                        continue
            
            # Update sale totals
            sale.subtotal = subtotal
            sale.total_gst = total_gst
            sale.total_amount = total_amount
            sale.save()
            
            # Update customer credit if sale is credit
            if sale.is_credit and sale.customer:
                from customers.models import CustomerCredit
                credit_obj, created = CustomerCredit.objects.get_or_create(customer=sale.customer)
                credit_obj.total_credit += sale.total_amount
                credit_obj.save()
            messages.success(request, f'Sale #{sale.invoice_number} created successfully!')
            return redirect('sales:sale_detail', pk=sale.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating sale: {str(e)}')
    
    customers = Customer.objects.all()
    products = Product.objects.all()
    return render(request, 'sales/sale_form.html', {
        'customers': customers,
        'products': products
    })

def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    # Calculate total profit for this sale
    total_profit = sum([item.profit for item in sale.items.all()])
    return render(request, 'sales/sale_detail.html', {'sale': sale, 'total_profit': total_profit})

def print_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/invoice.html', {'sale': sale})

def edit_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    customers = Customer.objects.all()
    products = Product.objects.all()
    return render(request, 'sales/sale_form.html', {
        'sale': sale,
        'customers': customers,
        'products': products
    })

def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        try:
            sale_id = sale.pk
            sale.delete()
            messages.success(request, f'Sale #{sale_id} deleted successfully!')
            return redirect('sales:sale_list')
        except Exception as e:
            messages.error(request, f'Error deleting sale: {str(e)}')
            return redirect('sales:sale_detail', pk=pk)
    return render(request, 'sales/sale_confirm_delete.html', {'sale': sale})

def today_sales(request):
    return render(request, 'sales/today_sales.html')
