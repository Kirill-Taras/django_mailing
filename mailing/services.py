from django.core.mail import send_mail
from django.conf import settings

def send_mailing(mailing):
    send_mail(
        subject=mailing.message.subject,
        message=mailing.message.body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[client.email for client in mailing.clients.all()],
    )
    if mailing.status == 'created':
        mailing.status = 'started'
        mailing.save()