=============================
Django Request Correlation
=============================

.. image:: https://badge.fury.io/py/dj-request-correlation.svg
    :target: https://badge.fury.io/py/dj-request-correlation

.. image:: https://travis-ci.org/cdcarter/dj-request-correlation.svg?branch=master
    :target: https://travis-ci.org/cdcarter/dj-request-correlation

.. image:: https://codecov.io/gh/cdcarter/dj-request-correlation/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/cdcarter/dj-request-correlation

Django support for X-Request-Id and other request correlation techniques. dj-request-correlation requires Python 3.7+ and Django 2.0+.

Quickstart
----------

Install Django Request Correlation::

    pip install dj-request-correlation

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'dj_request_correlation.apps.DjRequestCorrelationConfig',
        ...
    )

Add Django Request Correlation's URL patterns:

.. code-block:: python

    from dj_request_correlation import urls as dj_request_correlation_urls


    urlpatterns = [
        ...
        url(r'^', include(dj_request_correlation_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
