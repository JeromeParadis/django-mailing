from __future__ import absolute_import
from django.conf import settings

from celery import shared_task

from .mail import send_email
from .shortcuts import render_send_email


from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(name="mailing.queue_send_email")
def queue_send_email(recipients, subject, text_content=None, html_content=None, from_email=settings.DEFAULT_FROM_EMAIL, use_base_template=True, category=None, fail_silently=False, language=None, cc=None, bcc=None, attachments=None, headers=None, bypass_hijacking=False, attach_files=None, reply_to=None): 
    
    logger.debug('Sending %s to %s' % (subject, ','.join(recipients), ))

    send_email(recipients=recipients, subject=subject, text_content=text_content, html_content=html_content, from_email=from_email, use_base_template=use_base_template, category=category, fail_silently=fail_silently, language=language, cc=cc, bcc=bcc, attachments=attachments, headers=headers, bypass_queue=True, bypass_hijacking=bypass_hijacking, attach_files=attach_files, reply_to=reply_to)

    return True

@shared_task(name="mailing.queue_render_send_email")
def queue_render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, use_base_template=True, category=None, fail_silently=False, language=None, cc=None, bcc=None, attachments=None, headers=None, bypass_hijacking=False, attach_files=None, reply_to=None):
    
    logger.debug('Rendering and sending %s to %s' % (template, ','.join(recipients), ))

    render_send_email(recipients=recipients, template=template, data=data, from_email=from_email, subject=subject, use_base_template=use_base_template, category=category, fail_silently=fail_silently, language=language, cc=cc, bcc=bcc, attachments=attachments, headers=headers, bypass_queue=True, bypass_hijacking=bypass_hijacking, attach_files=attach_files, reply_to=reply_to)

    return True
