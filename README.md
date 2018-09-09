# dj-request-correlation

[![pypi badge](https://badge.fury.io/py/dj-request-correlation.svg)](https://badge.fury.io/py/dj-request-correlation)

[![travis badge](https://travis-ci.org/cdcarter/dj-request-correlation.svg?branch=master)](https://travis-ci.org/cdcarter/dj-request-correlation)

[![coverage badge](https://codecov.io/gh/cdcarter/dj-request-correlation/branch/master/graph/badge.svg)](https://codecov.io/gh/cdcarter/dj-request-correlation)

Django support for X-Request-Id and other request correlation techniques. **dj-request-correlation requires Python 3.7+ and Django 2.0+.**

*What is X-Request-Id?*

> When you're operating a webservice that is accessed by clients, it might be difficult to correlate requests (that a client can see) with server logs (that the server can see).
>The idea of the X-Request-ID is that a client can create some random ID and pass it to the server. The server then include that ID in every log statement that it creates. If a client receives an error it can include the ID in a bug report, allowing the server operator to look up the corresponding log statements (without having to rely on timestamps, IPs, etc).
> As this ID is generated (randomly) by the client it does not contain any sensitive information, and should thus not violate the user's privacy. As a unique ID is created per request it does also not help with tracking users.

Thanks to Stefan Kögl for that fantastic answer: https://stackoverflow.com/questions/25433258/what-is-the-x-request-id-http-header

The "definitive" implementation of X-Request-Id is [the one used by Heroku](https://devcenter.heroku.com/articles/http-request-id) and dj-request-correlation defaults to using that header.

# Quickstart

Install dj-request-correlation:

    pip install dj-request-correlation

Then, add the middleware to the top of your `MIDDLEWARE` setting:

```
    MIDDLEWARE = (
        'dj_request_correlation.middleware.RequestIDMiddleware',
        'django.middleware.security.SecurityMiddleware',
        ...
    )
```

As the package grows, I'll first be focusing on implementing the core featureset I want, before coming up with an easier setup/configuration mechanism. This means that for now, you'll need to configure each feature one at a time.

# Features

## RequestIDMiddleware
* Accept a client provided request correlation ID, and pass it to your Django views.
* Make the request correlation ID available in a global ContextVar for loggers and other code that doesn't get an explicit request object.
* Generate a UUID for the request if one wasn't provided by the client (or router).

## `dj_request_correlation.utils.logfmt` helper
* Turn a dict of `kwargs` into the "unofficial" [logfmt](https://brandur.org/logfmt) output format, which is also [recommended by Splunk](http://dev.splunk.com/view/logging-best-practices/SP-CAAAFCK) for automatic field extraction.

# Running Tests

Does the code actually work?

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ py.test

# Credits

Tools used in rendering this package:

* [cookiecutter](https://github.com/audreyr/cookiecutter)
* [cookiecutter-djangopackage](https://github.com/pydanny/cookiecutter-djangopackage)

Inspiration drawn from:

* [django-log-request-id](https://github.com/dabapps/django-log-request-id)
* [django-request-id](https://github.com/nigma/django-request-id/)