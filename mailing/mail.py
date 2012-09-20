from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string

# Define exception classes
# --------------------------------
class MailerInvalidBodyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MailerMissingSubjectError(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value if value else '')

def send_email_default(*args, **kwargs):
    send_email(args[3],args[0],args[1],args[1],args[2], category='django core email')

def send_email(recipients, subject, text_content=None, html_content=None, from_email=None, category=None, fail_silently=False, bypass_queue=False):
    """
    Will send a multi-format email to recipients. Email may be queued through celery
    """
    from django.conf import settings

    if not bypass_queue and hasattr(settings, 'MAILING_USE_CELERY') and settings.MAILING_USE_CELERY:
        from celery.execute import send_task
        return send_task('mailing.queue_send_email',[recipients, subject, text_content, html_content, from_email, category, fail_silently])
    else:
        # Check for sendgrid support and add category header
        # --------------------------------
        if hasattr(settings, 'MAILING_USE_SENDGRID'):
            send_grid_support = settings.MAILING_USE_SENDGRID
        else:
            send_grid_support = False
        
        if send_grid_support and category:
            headers = {'X-SMTPAPI': '{"category": "%s"}' % category}
        else:
            headers = dict()

        # Ensure recipients are in a list
        # --------------------------------
        if isinstance(recipients, basestring):
            recipients_list = [recipients]
        else:
            recipients_list = recipients

        # Check if we need to hijack the email
        # --------------------------------
        if hasattr(settings, 'MAILING_MAILTO_HIJACK'):
            headers['X-MAILER-ORIGINAL-MAILTO'] = ','.join(recipients_list)
            recipients_list = [settings.MAILING_MAILTO_HIJACK]

        if not subject:
            raise MailerMissingSubjectError('Subject not supplied')

        # Send ascii, html or multi-part email
        # --------------------------------
        if text_content or html_content:
            text_content = render_to_string('mailing/base.txt', {'content': text_content}) if text_content else None
            html_content = render_to_string('mailing/base.html', {'content': html_content}) if html_content else None
            msg = EmailMultiAlternatives(subject, text_content if text_content else html_content, from_email if from_email else settings.DEFAULT_FROM_EMAIL, recipients_list, headers = headers)
            if html_content and text_content:
                msg.attach_alternative(html_content, "text/html")
            elif html_content: # Only HTML
                msg.content_subtype = "html"
            msg.send(fail_silently=fail_silently)
        else:
            raise MailerInvalidBodyError('No text or html body supplied')
