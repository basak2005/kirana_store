from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('add/', views.add_customer, name='add_customer'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    path('<int:pk>/delete/', views.delete_customer, name='delete_customer'),
    path('credit-report/', views.credit_report, name='credit_report'),
]
