from django.core.mail import send_mail
from django.conf import settings

from mailing.models import MailingAttempt


def send_mailing(mailing):
    """Отправляет рассылку и логирует попытки"""
    clients = mailing.clients.all()
    message = mailing.message
    for client in clients:
        try:
            send_mail(
                subject=message.subject,
                message=message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
            )
            status = 'success'
            response = 'Письмо доставлено'
        except Exception as e:
            status = 'failed'
            response = str(e)

        MailingAttempt.objects.create(
            mailing=mailing,
            client=client,
            status=status,
            server_response=response,
        )

    if mailing.status == 'created':
        mailing.status = 'started'
        mailing.save()
