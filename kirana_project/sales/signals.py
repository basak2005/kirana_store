from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Sale
from reports.models import DailyReport
from datetime import date
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Sale)
def update_daily_report_on_sale(sender, instance, created, **kwargs):
    """Update daily report when a sale is created or modified"""
    try:
        sale_date = instance.date.date() if hasattr(instance.date, 'date') else instance.date
        DailyReport.generate_report(sale_date)
        logger.info(f"Daily report updated for sale #{instance.invoice_number}")
    except Exception as e:
        logger.error(f"Failed to update daily report for sale #{instance.invoice_number}: {e}")

@receiver(post_delete, sender=Sale)
def update_daily_report_on_sale_delete(sender, instance, **kwargs):
    """Update daily report when a sale is deleted"""
    try:
        sale_date = instance.date.date() if hasattr(instance.date, 'date') else instance.date
        DailyReport.generate_report(sale_date)
        logger.info(f"Daily report updated after deleting sale #{instance.invoice_number}")
    except Exception as e:
        logger.error(f"Failed to update daily report after deleting sale #{instance.invoice_number}: {e}")
