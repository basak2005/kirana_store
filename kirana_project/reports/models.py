from django.db import models
from django.db.models import Sum
from django.utils import timezone

class DailyReport(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_credit_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash_in_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Daily Report - {self.date}"

    @classmethod
    def generate_report(cls, date):
        """Generate or update daily report for given date"""
        from sales.models import Sale
        from suppliers.models import PurchaseOrder, Expense
        
        # Calculate sales data
        sales_data = Sale.objects.filter(date__date=date).aggregate(
            total_sales=Sum('total_amount'),
            credit_sales=Sum('total_amount', filter=models.Q(is_credit=True))
        )
        
        total_sales = sales_data['total_sales'] or 0
        credit_sales = sales_data['credit_sales'] or 0
        
        # Calculate purchase data
        purchases_data = PurchaseOrder.objects.filter(
            date__date=date, 
            status='completed'
        ).aggregate(total_purchases=Sum('total_amount'))
        
        total_purchases = purchases_data['total_purchases'] or 0
        
        # Calculate expenses
        expenses_data = Expense.objects.filter(date=date).aggregate(
            total_expenses=Sum('amount')
        )
        
        total_expenses = expenses_data['total_expenses'] or 0
        
        # Calculate profits
        gross_profit = total_sales - total_purchases
        net_profit = gross_profit - total_expenses
        cash_in_hand = total_sales - credit_sales
        
        # Create or update report
        report, created = cls.objects.update_or_create(
            date=date,
            defaults={
                'total_sales': total_sales,
                'total_purchases': total_purchases,
                'total_expenses': total_expenses,
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'total_credit_sales': credit_sales,
                'cash_in_hand': cash_in_hand,
            }
        )
        
        return report

    class Meta:
        ordering = ['-date']


class MonthlyReport(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    average_daily_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    best_selling_day = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Monthly Report - {self.month}/{self.year}"

    @classmethod
    def generate_report(cls, year, month):
        """Generate monthly report from daily reports"""
        daily_reports = DailyReport.objects.filter(
            date__year=year,
            date__month=month
        )
        
        if not daily_reports.exists():
            return None
        
        totals = daily_reports.aggregate(
            total_sales=Sum('total_sales'),
            total_purchases=Sum('total_purchases'),
            total_expenses=Sum('total_expenses'),
            gross_profit=Sum('gross_profit'),
            net_profit=Sum('net_profit')
        )
        
        # Find best selling day
        best_day_report = daily_reports.order_by('-total_sales').first()
        best_selling_day = best_day_report.date if best_day_report else None
        
        # Calculate average daily sales
        days_count = daily_reports.count()
        avg_daily_sales = totals['total_sales'] / days_count if days_count > 0 else 0
        
        report, created = cls.objects.update_or_create(
            year=year,
            month=month,
            defaults={
                'total_sales': totals['total_sales'] or 0,
                'total_purchases': totals['total_purchases'] or 0,
                'total_expenses': totals['total_expenses'] or 0,
                'gross_profit': totals['gross_profit'] or 0,
                'net_profit': totals['net_profit'] or 0,
                'average_daily_sales': avg_daily_sales,
                'best_selling_day': best_selling_day,
            }
        )
        
        return report

    class Meta:
        unique_together = ['year', 'month']
        ordering = ['-year', '-month']
