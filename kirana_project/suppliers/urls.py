from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('add/', views.add_supplier, name='add_supplier'),
    path('<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('<int:pk>/edit/', views.edit_supplier, name='edit_supplier'),
    path('<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
    path('purchase-orders/', views.purchase_orders, name='purchase_orders'),
    path('purchase-orders/new/', views.new_purchase, name='new_purchase'),
    path('purchase-orders/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchase-orders/<int:pk>/edit/', views.edit_purchase, name='edit_purchase'),
    path('purchase-orders/<int:pk>/delete/', views.delete_purchase_order, name='delete_purchase_order'),
    path('purchase-orders/<int:pk>/complete/', views.mark_as_completed, name='mark_as_completed'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
]
