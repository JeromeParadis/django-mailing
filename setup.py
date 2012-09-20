from distutils.core import setup

setup(
    name="django-mailing",
    version=__import__("mailing").__version__,
    description="A flexible Django app for templated mailings with support for celery queuing, SendGrid and more.",
    long_description=open("docs/usage.txt").read(),
    author="Jerome Paradis",
    author_email="jparadis@paradivision.com",
    url="http://github.com/JeromeParadis/django-mailing",
    packages=[
        "mailing",
    ],
    package_dir={"mailing": "mailing"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)