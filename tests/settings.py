# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.test.runner import DiscoverRunner


class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation/deletion """

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass


TEST_RUNNER = "tests.settings.NoDbTestRunner"

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "_+58z8d27&^9t-fuhe8&1$b&8f-%jm8f_p_2y47^!k0qd45#q("

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

ROOT_URLCONF = []

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
]

SITE_ID = 1

MIDDLEWARE = ("dj_request_correlation.middleware.RequestIDMiddleware",)
