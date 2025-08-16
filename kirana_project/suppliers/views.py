def delete_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        try:
            order.delete()
            messages.success(request, f'Purchase Order #{order.po_number} deleted successfully!')
            return redirect('suppliers:purchase_orders')
        except Exception as e:
            messages.error(request, f'Error deleting purchase order: {str(e)}')
            return redirect('suppliers:purchase_detail', pk=pk)
    return render(request, 'suppliers/purchase_detail.html', {'order': order})
from django.views.decorators.http import require_POST
@require_POST
def mark_as_completed(request, pk):
    from products.models import Product
    order = get_object_or_404(PurchaseOrder, pk=pk)
    from django.db import transaction
    if order.status != 'completed':
        try:
            with transaction.atomic():
                for item in order.items.all():
                    product = item.product
                    old_stock = product.stock
                    product.stock += item.quantity
                    try:
                        product.save(update_fields=['stock'])
                        # Confirm update
                        refreshed = Product.objects.get(pk=product.pk)
                        print(f"Updated stock for {product.name}: {old_stock} -> {product.stock} (DB: {refreshed.stock})")
                        if refreshed.stock != product.stock:
                            print(f"ERROR: Stock not updated in DB for {product.name}. Expected {product.stock}, got {refreshed.stock}")
                    except Exception as err:
                        print(f"ERROR saving stock for {product.name}: {err}")
                order.status = 'completed'
                order.save(update_fields=['status'])
            messages.success(request, f'Purchase Order #{order.po_number} marked as completed and stock updated.')
        except Exception as e:
            messages.error(request, f'Error updating stock: {str(e)}')
    else:
        messages.info(request, f'Purchase Order #{order.po_number} is already completed.')
    return redirect('suppliers:purchase_detail', pk=order.pk)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Supplier, PurchaseOrder, PurchaseItem, Expense
from django.db import models

# Create your views here.
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    total_suppliers = suppliers.count()
    active_suppliers = suppliers.filter(is_active=True).count()
    inactive_suppliers = suppliers.filter(is_active=False).count()
    # For pending orders and total purchases, you can add logic if needed
    pending_orders = PurchaseOrder.objects.filter(status='pending').count() if hasattr(PurchaseOrder, 'status') else 0
    total_purchases = PurchaseOrder.objects.aggregate(total=models.Sum('total_amount'))['total'] or 0
    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers,
        'total_suppliers': total_suppliers,
        'active_suppliers': active_suppliers,
        'inactive_suppliers': inactive_suppliers,
        'pending_orders': pending_orders,
        'total_purchases': total_purchases,
    })

def add_supplier(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            contact_person = request.POST.get('contact_person', '')
            phone = request.POST.get('phone')
            email = request.POST.get('email', '')
            address = request.POST.get('address')
            gst_number = request.POST.get('gst_number', '')
            is_active = request.POST.get('is_active') == 'on'
            
            # Validate required fields
            if not name or not phone or not address:
                messages.error(request, 'Please fill in all required fields (Name, Phone, Address).')
                return render(request, 'suppliers/supplier_form.html')
            
            # Create and save supplier
            supplier = Supplier.objects.create(
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email if email else None,
                address=address,
                gst_number=gst_number,
                is_active=is_active
            )
            
            messages.success(request, f'Supplier "{name}" added successfully!')
            return redirect('suppliers:supplier_list')
        except Exception as e:
            messages.error(request, f'Error adding supplier: {str(e)}')
    return render(request, 'suppliers/supplier_form.html')

def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'suppliers/supplier_detail.html', {'supplier': supplier})

def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        try:
            # Get form data
            supplier.name = request.POST.get('name')
            supplier.contact_person = request.POST.get('contact_person', '')
            supplier.phone = request.POST.get('phone')
            supplier.email = request.POST.get('email', '') or None
            supplier.address = request.POST.get('address')
            supplier.gst_number = request.POST.get('gst_number', '')
            supplier.is_active = request.POST.get('is_active') == 'on'
            
            # Validate required fields
            if not supplier.name or not supplier.phone or not supplier.address:
                messages.error(request, 'Please fill in all required fields (Name, Phone, Address).')
                return render(request, 'suppliers/supplier_form.html', {'supplier': supplier})
            
            supplier.save()
            
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('suppliers:supplier_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error updating supplier: {str(e)}')
    return render(request, 'suppliers/supplier_form.html', {'supplier': supplier})

def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        try:
            supplier_name = supplier.name
            supplier.delete()
            messages.success(request, f'Supplier "{supplier_name}" deleted successfully!')
            return redirect('suppliers:supplier_list')
        except Exception as e:
            messages.error(request, f'Error deleting supplier: {str(e)}')
            return redirect('suppliers:supplier_detail', pk=pk)
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})

def purchase_orders(request):
    orders = PurchaseOrder.objects.all().order_by('-date')
    return render(request, 'suppliers/purchase_orders.html', {'orders': orders})

def new_purchase(request):
    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('supplier')
            supplier = Supplier.objects.get(pk=supplier_id)
            expected_delivery = request.POST.get('expected_delivery') or None
            notes = request.POST.get('notes', '')

            order = PurchaseOrder.objects.create(
                supplier=supplier,
                total_amount=0,
                subtotal=0,
                total_gst=0,
                expected_delivery=expected_delivery,
                notes=notes,
                status='pending'
            )

            products_ids = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')
            costs = request.POST.getlist('cost[]')
            gsts = request.POST.getlist('gst[]')

            subtotal = 0
            total_gst = 0
            total_amount = 0

            from products.models import Product
            for idx, prod_id in enumerate(products_ids):
                if not prod_id:
                    continue
                product = Product.objects.get(pk=prod_id)
                quantity = int(quantities[idx]) if idx < len(quantities) else 1
                unit_cost = float(costs[idx]) if idx < len(costs) else float(product.cost_price)
                gst_rate = float(gsts[idx]) if idx < len(gsts) else float(product.gst_rate)

                base_amount = quantity * unit_cost
                gst_amount = (base_amount * gst_rate) / 100
                total_cost = base_amount + gst_amount

                PurchaseItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    gst_rate=gst_rate,
                    gst_amount=gst_amount,
                    total_cost=total_cost
                )

                # Update product stock immediately
                product.stock += quantity
                product.save(update_fields=['stock'])

                subtotal += base_amount
                total_gst += gst_amount
                total_amount += total_cost

            order.subtotal = subtotal
            order.total_gst = total_gst
            order.total_amount = total_amount
            order.save()

            messages.success(request, f'Purchase Order #{order.po_number} created successfully!')
            return redirect('suppliers:purchase_detail', pk=order.pk)
        except Exception as e:
            messages.error(request, f'Error creating purchase order: {str(e)}')

    from products.models import Product
    suppliers = Supplier.objects.all()
    products = Product.objects.filter(is_active=True)
    return render(request, 'suppliers/purchase_form.html', {'suppliers': suppliers, 'products': products})

def purchase_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'suppliers/purchase_detail.html', {'order': order})

def expense_list(request):
    expenses = Expense.objects.all().order_by('-created_at')
    return render(request, 'suppliers/expense_list.html', {'expenses': expenses})

def add_expense(request):
    return render(request, 'suppliers/expense_form.html')
