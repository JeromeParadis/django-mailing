from django.conf import settings

from celery.task import task

from mail import send_email
from shortcuts import render_send_email

@task(name="mailing.queue_send_email")
def queue_send_email(recipients, subject, text_content=None, html_content=None, from_email=settings.DEFAULT_FROM_EMAIL, use_base_template=True, category=None, fail_silently=False, language=None): 
    
    logger = queue_send_email.get_logger()
    logger.debug('Sending %s to %s' % (subject, ','.join(recipients), ))

    send_email(recipients=recipients, subject=subject, text_content=text_content, html_content=html_content, from_email=from_email, use_base_template=use_base_template, category=category, fail_silently=fail_silently, language=language, bypass_queue=True)

    return True

@task(name="mailing.queue_render_send_email")
def queue_render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, use_base_template=True, category=None, fail_silently=False, language=None):
    
    logger = queue_render_send_email.get_logger()

    logger.debug('Rendering and sending %s to %s' % (template, ','.join(recipients), ))

    render_send_email(recipients=recipients, template=template, data=data, from_email=from_email, subject=subject, use_base_template=use_base_template, category=category, fail_silently=fail_silently, language=language, bypass_queue=True)

    return True
