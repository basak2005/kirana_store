from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseItem)
admin.site.register(Expense)
