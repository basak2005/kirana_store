from django.db import models
from django.core.validators import MinValueValidator

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    gst_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"PO #{self.po_number} - {self.supplier.name} - ₹{self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            # Generate PO number
            last_po = PurchaseOrder.objects.order_by('-id').first()
            if last_po:
                last_number = int(last_po.po_number.split('-')[-1])
                self.po_number = f"PO-{last_number + 1:06d}"
            else:
                self.po_number = "PO-000001"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']


class PurchaseItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate GST amount
        base_amount = self.quantity * self.unit_cost
        self.gst_amount = (base_amount * self.gst_rate) / 100
        self.total_cost = base_amount + self.gst_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} = ₹{self.total_cost}"

    class Meta:
        ordering = ['id']


class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('rent', 'Shop Rent'),
        ('electricity', 'Electricity Bill'),
        ('water', 'Water Bill'),
        ('internet', 'Internet/Phone Bill'),
        ('salary', 'Staff Salary'),
        ('transport', 'Transportation'),
        ('maintenance', 'Shop Maintenance'),
        ('office_supplies', 'Office Supplies'),
        ('advertising', 'Advertising/Marketing'),
        ('insurance', 'Insurance'),
        ('tax', 'Taxes & Fees'),
        ('other', 'Other Expenses'),
    ]

    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - ₹{self.amount} ({self.date})"

    class Meta:
        ordering = ['-date', '-created_at']
