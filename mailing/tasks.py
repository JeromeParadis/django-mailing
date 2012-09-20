from django.conf import settings

from celery.task import task

from mail import send_email
from shortcuts import render_send_email

@task(name="mailing.queue_send_email")
def queue_send_email(recipients, subject, text_content=None, html_content=None, from_email=settings.DEFAULT_FROM_EMAIL, category=None, fail_silently=False): 
    
    logger = queue_send_email.get_logger()
    logger.debug('Sending %s to %s' % (subject, ','.join(recipients), ))

    send_email(recipients=recipients, subject=subject, text_content=text_content, html_content=html_content, from_email=from_email, category=category, fail_silently=fail_silently, bypass_queue=True)

    return True

@task(name="mailing.queue_render_send_email")
def queue_render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, category=None, fail_silently=False, language='en'):
    
    logger = queue_render_send_email.get_logger()

    logger.debug('Rendering and sending %s to %s' % (template, ','.join(recipients), ))

    render_send_email(recipients=recipients, template=template, data=data, from_email=from_email, subject=subject, category=category, fail_silently=fail_silently, language=language, bypass_queue=True)

    return True
