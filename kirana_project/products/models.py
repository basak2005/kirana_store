from django.db import models

class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']


class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilogram'),
        ('gram', 'Gram'),
        ('litre', 'Litre'),
        ('ml', 'Millilitre'),
        ('packet', 'Packet'),
        ('box', 'Box'),
        ('bottle', 'Bottle'),
    ]

    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True)
    barcode = models.CharField(max_length=50, blank=True, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=5)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default="pcs")
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.brand})" if self.brand else self.name

    @property
    def is_low_stock(self):
        return self.stock <= self.min_stock_level

    @property
    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0

    class Meta:
        ordering = ['name']
