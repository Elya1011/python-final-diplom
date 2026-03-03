from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import URLValidator
from requests import get
from yaml import load as load_yaml, Loader

from .models import (ConfirmEmailToken, OrderItem, Contact, Shop, Category, Product, ProductInfo, Parameter,
                     ProductParameter)

User = get_user_model()


@shared_task
def send_password_reset_email(user_email, token_key):
    """Отправка письма для сброса пароля"""
    msg = EmailMultiAlternatives(
        f"Password Reset Token for {user_email}",
        token_key,
        settings.EMAIL_HOST_USER,
        [user_email]
    )
    msg.send()
    return f"Password reset email sent to {user_email}"


@shared_task
def send_confirmation_email(user_id):
    """Отправка письма для подтверждения email"""
    try:
        user = User.objects.get(id=user_id)
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
        
        msg = EmailMultiAlternatives(
            f"Email Confirmation for {user.email}",
            token.key,
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        msg.send()
        return f"Confirmation email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


@shared_task
def send_order_status_email(user_id, message):
    """Отправка уведомления о статусе заказа"""
    try:
        user = User.objects.get(id=user_id)
        msg = EmailMultiAlternatives(
            "Обновление статуса заказа",
            message,
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        msg.send()
        return f"Order status email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


@shared_task
def import_price_list_task(user_id, url):
    """Импорт прайс-листа для магазина"""
    try:
        
        user = User.objects.get(id=user_id)
        
        if user.type != 'shop':
            return f"User {user.email} is not a shop"
        
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError as e:
            return f"Invalid URL: {str(e)}"
        
        stream = get(url).content
        data = load_yaml(stream, Loader=Loader)
        
        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=user_id)
        
        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
            
            product_info = ProductInfo.objects.create(
                product_id=product.id,
                external_id=item['id'],
                model=item['model'],
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity'],
                shop_id=shop.id
            )
            
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=parameter_object.id,
                    value=value
                )
        
        return f"Price list imported successfully for shop {shop.name}"
        
    except User.DoesNotExist:
        return f"User with id {user_id} not found"
    except Exception as e:
        return f"Error importing price list: {str(e)}"


@shared_task
def mass_delete_task(model_name, filter_kwargs):
    """Массовое удаление объектов по параметрам"""
    try:
        
        if model_name == 'OrderItem':
            deleted_count = OrderItem.objects.filter(**filter_kwargs).delete()[0]
            return f"Deleted {deleted_count} OrderItem objects"
        elif model_name == 'Contact':
            deleted_count = Contact.objects.filter(**filter_kwargs).delete()[0]
            return f"Deleted {deleted_count} Contact objects"
        else:
            return f"Unsupported model: {model_name}"
            
    except Exception as e:
        return f"Error in mass delete: {str(e)}"