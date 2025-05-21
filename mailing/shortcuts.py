from __future__ import absolute_import
from django.conf import settings
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils import translation
from django.template.context import make_context
from django.template.loader import get_template

from mailing.mail import send_email

def render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, use_base_template=True, category=None, fail_silently=False, language=None, cc=None, bcc=None, attachments=None, headers=None, bypass_queue=False, bypass_hijacking=False, attach_files=None, reply_to=None, options=None):
    if not bypass_queue and hasattr(settings, 'MAILING_USE_CELERY') and settings.MAILING_USE_CELERY:
        from celery.execute import send_task
        return send_task('mailing.queue_render_send_email',[recipients, template, data, from_email, subject, use_base_template, category, fail_silently, language if language else translation.get_language(), cc, bcc, attachments, headers, bypass_hijacking, attach_files, reply_to, options])
    else:
        # Set language
        # --------------------------------
        prev_language = translation.get_language()
        language and translation.activate(language)

        templated_subject, templated_text, templated_html = render_template(template, data)
        if subject:
            my_subject = subject
        elif templated_subject:
            my_subject = templated_subject
        else:
            my_subject = None
        if not data:
            data = dict()
        if use_base_template and my_subject and 'mailing_subject' not in data:
            data['mailing_subject'] = my_subject
        if 'settings' not in data:
            data['settings'] = settings
        if templated_text:
            text_content = templated_text
        else:
            text_content = None
        if templated_html:
            html_content = templated_html
        else:
            html_content = None

        translation.activate(prev_language)
        send_email(recipients, my_subject, text_content, html_content, from_email, use_base_template, category, fail_silently=fail_silently, language=language, cc=cc, bcc=bcc, attachments=attachments, headers=headers, bypass_queue=True, bypass_hijacking=bypass_hijacking, attach_files=attach_files, reply_to=reply_to, options=options)
        

def render_template(template_path, data):
    """
    Renders the template with the given data and returns the rendered subject, text, and html content.
    If the supplied template has a .html extension, then it is assumed to be a single template with a subject, text, and html in the same style than Djoser templates.
    If the supplied template does not have an extension, then it is assumed to point to multiple templates with a subject, text, and html. 
    """
    templated_subject, templated_text, templated_html = None, None, None
    if template_path:
        if template_path.endswith('.html'):
            _node_map = {
                "subject": "subject",
                "text_body": "body",
                "html_body": "html",
            }
            context = make_context(data)
            template = get_template(template_path)
            with context.bind_template(template.template):
                for node in template.template.nodelist:
                    attr = _node_map.get(getattr(node, "name", ""))
                    if attr is not None:
                        if attr == "subject":
                            templated_subject = node.render(context).strip()
                        elif attr == "body":
                            templated_text = node.render(context).strip()
                        elif attr == "html":
                            templated_html = node.render(context).strip()
                        else:
                            # Handle other attributes if needed
                            pass
        else:
            try:
                templated_subject = render_to_string('%s.subject' % template_path, data)
            except TemplateDoesNotExist:
                pass

            try:
                templated_text = render_to_string('%s.txt' % template_path, data)
            except TemplateDoesNotExist:
                pass
            try:
                templated_html = render_to_string('%s.html' % template_path, data)
            except TemplateDoesNotExist:
                pass

    return templated_subject, templated_text, templated_html
