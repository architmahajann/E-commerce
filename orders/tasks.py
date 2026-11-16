from celery import shared_task

from .models import Order
from .utils import send_order_notification


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_order_notification_task(order_id):
    order = Order.objects.select_related('user').get(pk=order_id)
    send_order_notification(order)
