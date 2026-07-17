from time import sleep

from celery import shared_task
from django.core.mail import send_mail

from .models import Category, Review


@shared_task
def notify_product_created(title):
    print(f"start task notify_product_created for '{title}'")
    sleep(5)

    return f"Product '{title}' created"



@shared_task
def delete_low_rated_reviews():
    deleted_count, _ = Review.objects.filter(stars__lte=2).delete()

    return f"Deleted {deleted_count} low-rated reviews"


@shared_task
def send_new_product_email(title, price):
    send_mail(
        subject="Новый товар в каталоге",
        message=f"Добавлен новый товар: {title}, цена: {price}",
        from_email="B-64-1",
        recipient_list=[
            "nodiraabd2007@gmail.com",
        ],
    )
    return "OK"



@shared_task
def notify_review_added(product_title, stars):
    print(f"start task notify_review_added for '{product_title}' ({stars})")
    sleep(5)

    return f"Review for '{product_title}' added"


@shared_task
def delete_empty_categories():
    deleted_count, _ = Category.objects.filter(product__isnull=True).distinct().delete()

    return f"Deleted {deleted_count} empty categories"


@shared_task
def send_new_category_email(name):
    send_mail(
        subject="Новая категория в каталоге",
        message=f"Добавлена новая категория: {name}",
        from_email="B-64-1",
        recipient_list=[
            "nodiraabd2007@gmail.com",
        ],
    )
    return "OK"