
=====
Usage
=====

django-mailing was developed to:
 * send emails in ASCII or HTML
 * support email templating with headers and footers
 * support multilingual environments
 * optionally use SendGrid to categorize email statistics and sync email lists
 * optionally support celery for queuing mail sending and/or processing in background processes

Installation
============

Available on PyPi::

    pip install django-mailing

Configuration
=============

Add to your installed apps in your setting.py file::

    INSTALLED_APPS = (
    ...
    'mailing',
    )

settings.DEFAULT_FROM_EMAIL
---------------------------

You need to set your default from email::

    DEFAULT_FROM_EMAIL = 'contact@mydomain.com'


settings.MAILING_USE_SENDGRID
-----------------------------

Boolean to indicate you have configured Django to use SendGrid::

    MAILING_USE_SENDGRID = True

The impact is you now have additional SendGrid capabilities such as the ability to:
 * categorize emails sent
 * manage/sync mailing lists (currently not implemented)
 * plus all the good stuff they do on their side.

settings.MAILING_MAILTO_HIJACK
------------------------------

You can hijack email sent by your app to redirect to another email. Quite practical when developing or testing with external email addresses::

    MAILING_MAILTO_HIJACK = 'me@mydomain.com'

If defined, every outgoind email will be sent to me@mydomain.com. For debugging/testing purposes, the following header is added to the email::

    X-MAILER-ORIGINAL-MAILTO: me@mydomain.com

It will contain what would have been the original "To" header if we hadn't hijacked it

settings.MAILING_USE_CELERY
---------------------------

Boolean indicating celery is configured and you want to send/process email related stuff in background::

    MAILING_USE_CELERY = True

For example, you can configure your app to use celery by installing a redis server.

Your settings would also need to include things like::

    INSTALLED_APPS = (
        #
        # ...
        #

        'celery',
        'djcelery',

        #
        # ...
        #

        'mailing',

        #
        # ...
        #
    )
    
    # 
    # ...
    #
    
    # Celery Configuration. Ref.: http://celery.github.com/celery/configuration.htm
    # -------------------------------------
    os.environ["CELERY_LOADER"] = "django"
    djcelery.setup_loader()

    BROKER_TRANSPORT = "redis"
    BROKER_HOST = "localhost"  # Maps to redis host.
    BROKER_PORT = 6379         # Maps to redis port.
    BROKER_VHOST = "0"         # Maps to database number.

    CELERY_IGNORE_RESULT = False
    CELERY_RESULT_BACKEND = "redis"
    CELERY_REDIS_HOST = "localhost"
    CELERY_REDIS_PORT = 6379
    CELERY_REDIS_DB = 0

When running the celery daemon, you need to include the ``mailing`` app in the tasks through the ``include`` parameter. Example::

    manage.py celeryd --verbosity=2 --beat --schedule=celery --events --loglevel=INFO -I mailing

You therefore could run a separate celery daemon to run your mailing tasks independently of other tasks if the need arises.

settings.MAILING_LANGUAGES
--------------------------

Not yet implemented.

Replacing the core django send_mail function
--------------------------------------------

To replace Django's core send_mail function to add support for email templates, SendGrid integration and background celery sending, add the following code to your settings file::

    import sys
    from mailing.mail import send_email_default
    try:
        from django.core import mail 
        mail.send_mail = send_email_default
        sys.modules['django.core.mail'] = mail
    except ImportError:
        pass


Using django-mailing
====================

Simple multi-part send_mail replacement
---------------------------------------

You can using mailing.send_email instead of Django's send_mail to send multi-part messages::

    send_email(recipients, subject, text_content=None, html_content=None, from_email=settings.DEFAULT_FROM_EMAIL, category=None, fail_silently=False, bypass_queue=False)

Parameters are:
 * ``recipients`` is a list of email addresses to send the email to
 * ``subject`` is the subject of your email
 * ``text_content`` is the ASCII content of the email
 * ``html_content`` is the HTML content of the email
 * ``from_email`` is a string and is the sender's address
 * ``category`` is a string and is used to define SendGrid's X-SMTPAPI's category header

You must supply at least text_content or html_content. If both aren't supplied, an exception will be raised. If only one of the two is supplied, the email will be sent in the corresponding format. If both content are supplied, a multi-part email will be sent.

Example usage::

    from mailing import send_email

    send_email(['test1@mydomain.com', 'test@mydomain.com'], 'Testing 1,2,3...', 'Text Body', 'HTML Body', category='testing')

Rendering and sending emails using templates
--------------------------------------------

To use Django templates to generate dynamic emails, similar to using ``render_with_context`` in a Django view, use the ``render_send_email`` shortcut::

    render_send_email(recipients, template, data, from_email=settings.DEFAULT_FROM_EMAIL, subject=None, category=None, fail_silently=False, language='en', bypass_queue=False)

Parameters are:
 * ``recipients`` is a list of email addresses to send the email to
 * ``template`` the path to your Django templates, without any extension
 * ``data`` data context dictionnary to render the template
 * ``from_email`` is a string and is the sender's address
 * ``subject`` is the subject of your email
 * ``category`` is a string and is used to define SendGrid's X-SMTPAPI's category header

Example::

    def send_welcome_email(user):
        from mailing.shortcuts import render_send_email
    
        render_send_email(['test1@mydomain.com', 'test@mydomain.com'], 'users/welcome', {'user': user}, category='welcome')

in your app, you would need the following template files with the right extensions:
 * ``templates/users/welcome.txt``
 * ``templates/users/welcome.html``
 * ``templates/users/welcome.subject``

The subject template file can be omitted but you then need to supply the ``subject`` parameter. If you do not create a template with a .txt or a .html extension, then the associated format won't be included in the email. So, if you want to only send ASCII messages, do not create a .html file.

Example without using a subject template::

    render_send_email(['test1@mydomain.com', 'test@mydomain.com'], 'app/welcome', data, subject='Welcome new user', category='welcome')

Templates
---------

The following templates are defined and used by django-mailing and should be overriten in your own templates:
 * ``templates/mailing/base.txt``
 * ``templates/mailing/base.html``

These are used to define your email overall look like the header and footer. The only requirement is to include the ``{{ content }}`` template variable. It is there than the supplied content of your email will be inserted in your base template.

LICENSE
=======

Copyright (c) 2009 Jerome Paradis, Alain Carpentier and contributors

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.