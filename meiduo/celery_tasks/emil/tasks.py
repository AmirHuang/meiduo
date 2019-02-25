from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import app


@app.task(name='send_email')
def send_email(subject, to_email, html_message):
    send_mail(subject, '', settings.EMAIL_FROM,
              [to_email], html_message=html_message)
