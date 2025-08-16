from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('new/', views.new_sale, name='new_sale'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('<int:pk>/invoice/', views.print_invoice, name='print_invoice'),
    path('<int:pk>/edit/', views.edit_sale, name='edit_sale'),
    path('<int:pk>/delete/', views.delete_sale, name='delete_sale'),
    path('today/', views.today_sales, name='today_sales'),
]
