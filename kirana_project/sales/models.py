from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Sale(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('credit', 'Credit'),
        ('mixed', 'Mixed Payment'),
    ]

    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='cash')
    is_credit = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        customer_name = self.customer.name if self.customer else "Walk-in Customer"
        return f"Sale #{self.invoice_number} - {customer_name} - ₹{self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            last_sale = Sale.objects.order_by('-id').first()
            if last_sale:
                last_number = int(last_sale.invoice_number.split('-')[-1])
                self.invoice_number = f"INV-{last_number + 1:06d}"
            else:
                self.invoice_number = "INV-000001"
        
        # Set credit flag based on payment mode
        self.is_credit = (self.payment_mode == 'credit')
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']


class SaleItem(models.Model):
    @property
    def profit(self):
        # Profit per item = (unit_price - cost_price) * quantity
        if self.product and hasattr(self.product, 'cost_price'):
            return (self.unit_price - self.product.cost_price) * self.quantity
        return 0
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate GST amount
        base_amount = self.quantity * self.unit_price
        self.gst_amount = (base_amount * self.gst_rate) / 100
        self.total_price = base_amount + self.gst_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} = ₹{self.total_price}"

    class Meta:
        ordering = ['id']
