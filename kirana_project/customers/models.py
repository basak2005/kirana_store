from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class CustomerCredit(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='credit')
    total_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - ₹{self.total_credit}"
