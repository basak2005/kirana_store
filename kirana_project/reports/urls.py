from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('monthly/', views.monthly_report, name='monthly_report'),
    path('yearly/', views.yearly_report, name='yearly_report'),
    path('sales-analysis/', views.sales_analysis, name='sales_analysis'),
    path('profit-loss/', views.profit_loss, name='profit_loss'),
    path('gst-report/', views.gst_report, name='gst_report'),
]
