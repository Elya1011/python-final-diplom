from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created
from .models import User
from .tasks import send_password_reset_email, send_confirmation_email, send_order_status_email


new_order = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created(reset_password_token, **_kwargs):
    """
    Отправляем письмо с токеном для сброса пароля через Celery
    :param reset_password_token: Token Model Object
    :return:
    """
    send_password_reset_email.delay(
        reset_password_token.user.email,
        reset_password_token.key
    )


@receiver(post_save, sender=User)
def new_user_registered_signal(instance: User, created: bool, **_kwargs):
    """
     отправляем письмо с подтверждением почты через Celery
    """
    if created and not instance.is_active:
        send_confirmation_email.delay(instance.pk)


@receiver(new_order)
def new_order_signal(user_id, **kwargs): # noqa: unused-argument
    """
    отправляем письмо при изменении статуса заказа через Celery
    """
    send_order_status_email.delay(user_id, 'Заказ сформирован')
