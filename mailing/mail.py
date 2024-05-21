from __future__ import absolute_import
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string
from django.utils import translation
import six
import json 

# Define exception classes
# --------------------------------
class MailerException(Exception):
    pass

class MailerConfigurationException(Exception):
    pass

class MailerInvalidBodyError(Exception):
    pass

class MailerMissingSubjectError(Exception):
    pass

def send_email_default(*args, **kwargs):
    send_email(args[3],args[0],args[1], from_email=args[2], category='django core email')

def send_email(recipients, subject, text_content=None, html_content=None, from_email=None, use_base_template=True, category=None, fail_silently=False, language=None, cc=None, bcc=None, attachments=None, headers=None, bypass_queue=False, bypass_hijacking=False, attach_files=None, reply_to=None, options=None):
    """
    Will send a multi-format email to recipients. Email may be queued through celery
    """
    from django.conf import settings
    if not bypass_queue and hasattr(settings, 'MAILING_USE_CELERY') and settings.MAILING_USE_CELERY:
        from celery.execute import send_task
        return send_task('mailing.queue_send_email',[recipients, subject, text_content, html_content, from_email, use_base_template, category, fail_silently, language if language else translation.get_language(), cc, bcc, attachments, headers, bypass_hijacking, attach_files, reply_to, options])
    else:

        header_category_value = '%s%s' % (settings.MAILING_HEADER_CATEGORY_PREFIX if hasattr(settings, 'MAILING_HEADER_CATEGORY_PREFIX') else '', category)
        # Check for sendgrid support and add category header
        # --------------------------------
        if hasattr(settings, 'MAILING_USE_SENDGRID'):
            send_grid_support = settings.MAILING_USE_SENDGRID
        else:
            send_grid_support = False

        if not headers:
            headers = dict()        
        if send_grid_support and category:
            if 'X-SMTPAPI' not in headers:
                headers['X-SMTPAPI'] = '{"category": "%s"}' % header_category_value
            else:
                xsmtpapi = headers['X-SMTPAPI']
                if type(xsmtpapi) == dict:
                    xsmtpapi['category'] = header_category_value
                    headers['X-SMTPAPI'] = json.dumps(xsmtpapi)

        # Check for Mailgun support and add label header
        # --------------------------------
        if hasattr(settings, 'MAILING_USE_MAILGUN'):
            mailgun_support = settings.MAILING_USE_MAILGUN
        else:
            mailgun_support = False

        if not headers:
            headers = dict()        
        if mailgun_support and category:
            headers['X-Mailgun-Tag'] = header_category_value


        # Ensure recipients are in a list
        # --------------------------------
        if isinstance(recipients, six.string_types):
            recipients_list = [recipients]
        else:
            recipients_list = recipients

        # Check if we need to hijack the email
        # --------------------------------
        if hasattr(settings, 'MAILING_MAILTO_HIJACK') and not bypass_hijacking:
            headers['X-MAILER-ORIGINAL-MAILTO'] = ','.join(recipients_list)
            recipients_list = [settings.MAILING_MAILTO_HIJACK]

        if not subject:
            raise MailerMissingSubjectError('Subject not supplied')

        # Send ascii, html or multi-part email
        # --------------------------------
        def get_connection():
            if options and options.get('connection_name', None):
                if options['connection_name'] in settings.EMAIL_CONNECTIONS:
                    params = settings.EMAIL_CONNECTIONS[options['connection_name']]
                    connection = mail.get_connection(
                        host=params.get('HOST', None),
                        port=params.get('PORT', None),
                        username=params.get('HOST_USER', None),
                        password=params.get('HOST_PASSWORD', None),
                        use_tls=params.get('USE_TLS', None),
                        use_ssl=params.get('USE_SSL', None),
                        timeout=params.get('TIMEOUT', None),
                        ssl_keyfile=params.get('SSL_KEYFILE', None),
                        ssl_certfile=params.get('SSL_CERTFILE', None)
                    )
                    if headers and 'X-SMTPAPI' in headers:
                        del headers['X-SMTPAPI']
                else:
                    raise MailerConfigurationException('Invalid connection name for email backend.')
            elif options and options.get('connection', None):
                connection = options['connection']
            else:
                connection = mail.get_connection()
            return connection

        # raise Exception(options, connection, settings.EMAIL_CONNECTIONS)

        if text_content or html_content:
            with get_connection() as connection:
                if use_base_template:
                    prev_language = translation.get_language()
                    language and translation.activate(language)
                    text_content = render_to_string('mailing/base.txt', {'mailing_text_body': text_content, 'mailing_subject': subject, 'settings': settings}) if text_content else None
                    html_content = render_to_string('mailing/base.html', {'mailing_html_body': html_content, 'mailing_subject': subject, 'settings': settings}) if html_content else None
                    translation.activate(prev_language)
                msg = EmailMultiAlternatives(subject, text_content if text_content else html_content, from_email if from_email else settings.DEFAULT_FROM_EMAIL, recipients_list, cc=cc, bcc=bcc, attachments=attachments, headers = headers, reply_to=reply_to, connection=connection)
                if html_content and text_content:
                    msg.attach_alternative(html_content, "text/html")
                elif html_content: # Only HTML
                    msg.content_subtype = "html"

                # Attach files through attach_files helper
                # --------------------------------
                if attach_files:
                    for att in attach_files:  # attachments are tuples of (filepath, mimetype, filename)
                        with open(att[0], 'rb') as f:
                            content = f.read()
                        msg.attach(att[2], content, att[1])

                # Send email
                # --------------------------------
                msg.send(fail_silently=fail_silently)
        else:
            raise MailerInvalidBodyError('No text or html body supplied.')
