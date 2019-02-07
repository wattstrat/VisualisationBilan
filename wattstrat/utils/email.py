from django.template.loader import render_to_string
from django.core import mail
from django.conf import settings

from envelope import settings as email_settings

def send_email(email_recipients, subject, body_template, context):
    from_email = email_settings.FROM_EMAIL

    context.update({
        'domain': settings.DOMAIN,
        'protocol': 'https',
    })
    message_body = render_to_string(body_template, context)

    message = mail.EmailMultiAlternatives(
        subject=subject,
        body=message_body,
        from_email=from_email,
        to=email_recipients
    )
    message.send()

def send_email_to_admin(subject, body_template, context):
    send_email(email_settings.EMAIL_RECIPIENTS, subject, body_template, context)

def send_email_to_user(user, subject, body_template, context):
    send_email([user.email], subject, body_template, context)
