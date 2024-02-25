from .models import Business, ProductShop
from datetime import datetime, timedelta
from config.celery import celery

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags



@celery.task
def send_email():
    shops = Business.objects.all()

    for shop in shops:
        recipient_email = shop.email

        today = datetime.now().date()
        five_days_from_today = today + timedelta(days=5)

        product_expriration_within_five_days = ProductShop.objects.filter(
            shop_id=shop.id,
            expiration_date__gte=today,
            expiration_date__lte=five_days_from_today
        )

        context = {
            'products': product_expriration_within_five_days
        }

        if product_expriration_within_five_days:
            html_msg = render_to_string('core/email.html', context=context)
            plain_msg = strip_tags(html_msg)

            message = EmailMultiAlternatives(
                subject='These products are about to expire',
                body=plain_msg,
                from_email=None,
                to=[recipient_email]
            )

            message.attach_alternative(html_msg, 'text/html')
            message.send() 


def alert_users():
    send_email()    