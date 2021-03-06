# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio App RDM is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration for Invenio App RDM.

As a flavour extension, Invenio-App-RDM doesn't define configuration
variables of its own, but rather forcefully sets other modules'
configuration variables.

Import below the configuration defined in other modules that should be
(forcefully) set in an InvenioRDM instance, e.g.:

    from invenio_rdm_records.config import *


The role of Invenio App RDM is to configure other modules a specific way.
These configurations can nevertheless be overridden by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``

WARNING: An instance should NOT install multiple flavour extensions since
         there would be no guarantee of priority anymore.
"""

from datetime import timedelta

from invenio_rdm_records.config import *
from invenio_app.config import APP_DEFAULT_SECURE_HEADERS


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Flask
# =====
# See https://flask.palletsprojects.com/en/1.1.x/config/

APP_ALLOWED_HOSTS = ['invenio-dev01.tugraz.at', 'localhost', '127.0.0.1']
"""Allowed hosts.

Since HAProxy and Nginx route all requests no matter the host header
provided, the allowed hosts variable is set to localhost. In production it
should be set to the correct host and it is strongly recommended to only
route correct hosts to the application.
"""

MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
"""Max upload size for form data via application/multipart-formdata."""

SECRET_KEY = "CHANGE_ME"
"""Flask secret key.

Each installation (dev, production, ...) needs a separate key.

SECURITY WARNING: keep the secret key used in production secret!
"""

SESSION_COOKIE_SECURE = True
"""Sets cookie with the secure flag by default."""

# Flask-Limiter
# =============
# https://flask-limiter.readthedocs.io/en/stable/#configuration

RATELIMIT_STORAGE_URL = "redis://localhost:6379/3"
"""Storage for ratelimiter."""

# Flask-Babel
# ===========
# See https://pythonhosted.org/Flask-Babel/#configuration

BABEL_DEFAULT_LOCALE = 'en'
"""Default locale (language)."""

BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
"""Default time zone."""

# Invenio-I18N
# ============
# See https://invenio-i18n.readthedocs.io/en/latest/configuration.html

# Other supported languages (do not include BABEL_DEFAULT_LOCALE in list).
# I18N_LANGUAGES = [
#     ('fr', _('French'))
# ]


# Invenio-Theme
# =============
# See https://invenio-theme.readthedocs.io/en/latest/configuration.html

BASE_TEMPLATE = 'invenio_app_rdm/page.html'
"""Global base template."""

COVER_TEMPLATE = 'invenio_theme/page_cover.html'
"""Cover page base template (used for e.g. login/sign-up)."""

SETTINGS_TEMPLATE = 'invenio_theme/page_settings.html'
"""Settings base template."""

THEME_FOOTER_TEMPLATE = 'invenio_app_rdm/footer.html'
"""Footer base template."""

THEME_FRONTPAGE = True
"""Use default frontpage."""

# THEME_FRONTPAGE_TEMPLATE = 'invenio_app_rdm/frontpage.html'
"""Frontpage template."""

THEME_FRONTPAGE_TITLE = _('The turn-key research data management repository')
"""Frontpage title."""

# commented see below on tugraz section
# THEME_HEADER_TEMPLATE = 'invenio_theme/header.html'


"""Header base template."""

# THEME_LOGO = 'images/invenio-rdm.png'
"""Theme logo."""

THEME_SITENAME = _('InvenioRDM: Turn-key Research Data Management Repository')
"""Site name."""

# Invenio-Mail / Flask-Mail
# =========================
# See https://pythonhosted.org/Flask-Mail/#configuring-flask-mail

MAIL_SUPPRESS_SEND = True
"""Disable email sending by default."""

# Flask-Collect
# =============
# See https://github.com/klen/Flask-Collect#setup

COLLECT_STORAGE = 'flask_collect.storage.file'
"""Static files collection method (defaults to copying files)."""

# Invenio-Accounts
# ================
# (Flask-Security, Flask-Login, Flask-Principal, Flask-KVSession)
# See https://invenio-accounts.readthedocs.io/en/latest/configuration.html
# See https://flask-security.readthedocs.io/en/3.0.0/configuration.html

ACCOUNTS_SESSION_REDIS_URL = 'redis://localhost:6379/1'
"""Redis session storage URL."""

ACCOUNTS_USERINFO_HEADERS = True
"""Enable session/user id request tracing.

This feature will add X-Session-ID and X-User-ID headers to HTTP response. You
MUST ensure that NGINX (or other proxies) removes these headers again before
sending the response to the client. Set to False, in case of doubt.
"""

SECURITY_EMAIL_SENDER = "info@inveniosoftware.org"
"""Email address used as sender of account registration emails."""

SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to Invenio App RDM!")
"""Email subject for account registration emails."""

# Invenio-Celery / Celery / Flask-Celeryext
# =========================================
# See https://invenio-celery.readthedocs.io/en/latest/configuration.html
# See docs.celeryproject.org/en/latest/userguide/configuration.html
# See https://flask-celeryext.readthedocs.io/en/latest/

BROKER_URL = "amqp://guest:guest@localhost:5672/"
"""URL of message broker for Celery 3 (default is RabbitMQ)."""

CELERY_BEAT_SCHEDULE = {
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
    'accounts': {
        'task': 'invenio_accounts.tasks.clean_session_table',
        'schedule': timedelta(minutes=60),
    }
}
"""Scheduled tasks configuration (aka cronjobs)."""

CELERY_BROKER_URL = BROKER_URL
"""Same as BROKER_URL to support Celery 4."""

CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
"""URL of backend for result storage (default is Redis)."""

# Flask-SQLAlchemy
# ================
# See https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/

SQLALCHEMY_DATABASE_URI = \
    'postgresql+psycopg2://invenio-app-rdm:invenio-app-rdm@localhost/' \
    'invenio-app-rdm'
"""Database URI including user and password.

Default value is provided to make module testing easier.
"""

# Invenio-JSONSchemas
# ===================
# See https://invenio-jsonschemas.readthedocs.io/en/latest/configuration.html

JSONSCHEMAS_HOST = '0.0.0.0'
"""Hostname used in URLs for local JSONSchemas."""

# OAI-PMH
# =======
# See https://github.com/inveniosoftware/invenio-oaiserver/blob/master/invenio_oaiserver/config.py  # noqa
# (Using GitHub because documentation site out-of-sync at time of writing)

OAISERVER_ID_PREFIX = 'oai:invenio-app-rdm.org:'
"""The prefix that will be applied to the generated OAI-PMH ids."""

# Flask-DebugToolbar
# ==================
# See https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available above

DEBUG_TB_INTERCEPT_REDIRECTS = False
"""Switches off incept of redirects by Flask-DebugToolbar."""

# Flask-Caching
# =============
# See https://flask-caching.readthedocs.io/en/latest/index.html#configuring-flask-caching  # noqa

CACHE_REDIS_URL = "redis://localhost:6379/0"
"""URL to connect to Redis server."""

CACHE_TYPE = "redis"
"""Use Redis caching object."""

# Invenio-Search
# ==============
# See https://invenio-search.readthedocs.io/en/latest/configuration.html

SEARCH_ELASTIC_HOSTS = [{"host": "localhost", "port": 9200}]
"""Elasticsearch hosts."""

# Invenio-Base
# ============
# See https://invenio-base.readthedocs.io/en/latest/api.html#invenio_base.wsgi.wsgi_proxyfix  # noqa

WSGI_PROXIES = 2
"""Correct number of proxies in front of your application."""

# Invenio-Records-UI
# ==================
# See https://invenio-records-ui.readthedocs.io/en/latest/configuration.html

RECORDS_UI_ENDPOINTS = {
    'recid': {
        'pid_type': 'recid',
        'record_class': 'invenio_records_files.api:Record',
        'route': '/records/<pid_value>',
        'template': 'invenio_app_rdm/record_view_page.html'
    },
    'recid_file': {
        'pid_type': 'recid',
        'record_class': 'invenio_records_files.api:Record',
        'route': '/records/<pid_value>/files/<path:filename>',
        'view_imp': 'invenio_records_files.utils.file_download_ui',
    },
    'recid_preview': {
        'pid_type': 'recid',
        'record_class': 'invenio_records_files.api:Record',
        'route': '/records/<pid_value>/preview/<path:filename>',
        'view_imp': 'invenio_previewer.views.preview',
    },
}
"""Records UI for RDM Records."""

# Invenio-Search-UI
# ==================
# See https://invenio-search-ui.readthedocs.io/en/latest/configuration.html

SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/invenio_app_rdm/results.html'
"""The search results template."""

SEARCH_UI_SEARCH_TEMPLATE = 'invenio_app_rdm/search.html'
""""Search page."""

# Invenio-Previewer
# =================
# See https://github.com/inveniosoftware/invenio-previewer/blob/master/invenio_previewer/config.py  # noqa

PREVIEWER_PREFERENCE = [
    'csv_dthreejs',
    'iiif_image',
    'simple_image',
    'json_prismjs',
    'xml_prismjs',
    'mistune',
    'pdfjs',
    'ipynb',
    'zip',
]
"""Preferred previewers."""

# Invenio-IIIF
# =================
# See https://invenio-iiif.readthedocs.io/en/latest/configuration.html

IIIF_PREVIEW_TEMPLATE = "invenio_app_rdm/iiif_preview.html"
"""Template for IIIF image preview."""

# --------------------------------------------------- TUGRAZ ---------------------------------------------------

# Logo
THEME_LOGO = "images/logo.svg"

THEME_FRONTPAGE_TEMPLATE = 'invenio_app_rdm/frontpage_home.html'

# icon used in login page.
TUG_ICON = "images/icons_use.png"

# Login page.
SECURITY_LOGIN_USER_TEMPLATE = 'invenio_app_rdm/accounts/login.html'

#: Disable Content Security Policy headers.
APP_DEFAULT_SECURE_HEADERS['content_security_policy'] = {}

# : this would be TUGRAZ header.
THEME_HEADER_TEMPLATE = 'invenio_app_rdm/header.html'

# ------------------------------------------ ShibbolethAuthenticator ----------------------------------------

# SHIBBOLETH_ISACTIVE = 'False'
"""uncomment this to use the login with Tugraz @ login.html"""

SHIBBOLETH_SERVICE_PROVIDER_CERTIFICATE = './docker/shibbolethAuthenticator/sp.crt'  # x509cert
"""Path to certificate."""

SHIBBOLETH_SERVICE_PROVIDER_PRIVATE_KEY = './docker/shibbolethAuthenticator/sp.key'  # private_key
"""Path to certificate private key."""

SHIBBOLETH_IDP_CERT = './docker/shibbolethAuthenticator/idp.crt'
""" Path to crt from Identity provider """

SHIBBOLETH_SERVICE_PROVIDER = dict(
    strict=True,
    debug=True,
    entity_id='https://invenio-dev01/shibboleth'
)

SHIBBOLETH_IDENTITY_PROVIDERS = dict(
    idp=dict(
        entity_id='https://sso.tugraz.at/idp/shibboleth',  # name of invenio something to get to know
        title='SSO TUGRAZ',
        sso_url='https://sso.tugraz.at/idp/profile/SAML2/Redirect/SSO',  # redirects to for authentication
        sso__Logout_url='https://sso.tugraz.at/slo/Logout',  # singleLogoutService
        mappings=dict(
            sn='urn:oid:2.5.4.4',
            givenName='urn:oid:2.5.4.42',
            eduPersonPrincipalName='urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
            mail="urn:oid:0.9.2342.19200300.100.1.3",
            # email='urn:oid:0.9.2342.19200300.100.1.3',
            # full_name='urn:oid:2.5.4.3',
            # user_unique_id='urn:oid:2.16.756.1.2.5.1.1.1',
        )
    )
)

SHIBBOLETH_STATE_EXPIRES = 300
"""Number of seconds after which the state token expires."""

