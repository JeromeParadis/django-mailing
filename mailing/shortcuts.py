from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation

from mail import send_email

def render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, use_base_template=True, category=None, fail_silently=False, language=None, bypass_queue=False):
    if not bypass_queue and hasattr(settings, 'MAILING_USE_CELERY') and settings.MAILING_USE_CELERY:
        from celery.execute import send_task
        return send_task('mailing.queue_render_send_email',[recipients, template, data, from_email, subject, use_base_template, category, fail_silently, language if language else translation.get_language()])
    else:
        # Set language
        # --------------------------------
        prev_language = translation.get_language()
        language and translation.activate(language)
        if subject:
            my_subject = subject
        else:
            try:
                my_subject = render_to_string('%s.subject' % template, data)
            except:
                my_subject = None
        if use_base_template and my_subject and 'mailing_subject' not in data:
            data['mailing_subject'] = my_subject
        try:
            text_content = render_to_string('%s.txt' % template, data)
        except:
            text_content = None

        try:
            html_content = render_to_string('%s.html' % template, data)
        except:
            html_content = None

        translation.activate(prev_language)

        send_email(recipients, my_subject, text_content, html_content, from_email, use_base_template, category, fail_silently=fail_silently, language=None, bypass_queue=True)
        