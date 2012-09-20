from django.conf import settings
from django.template.loader import render_to_string

from mail import send_email

def render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, category=None, fail_silently=False, language='en', bypass_queue=False):
    if not bypass_queue and hasattr(settings, 'MAILING_USE_CELERY') and settings.MAILING_USE_CELERY:
        from celery.execute import send_task
        return send_task('mailing.queue_render_send_email',[recipients, template, data, from_email, subject, category, fail_silently, language])
    else:
        try:
            text_content = render_to_string('%s.txt' % template, data)
        except:
            text_content = None

        try:
            html_content = render_to_string('%s.html' % template, data)
        except:
            html_content = None

        if subject:
            my_subject = subject
        else:
            try:
                my_subject = render_to_string('%s.subject' % template, data)
            except:
                my_subject = None

        send_email(recipients, my_subject, text_content, html_content, from_email, category, fail_silently=fail_silently, bypass_queue=True)
        