#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_dj-request-correlation
------------

Tests for `dj-request-correlation` models module.
"""

from django.test import SimpleTestCase


class TestLoadedMiddleware(SimpleTestCase):
    """ An integration test that actually loads and uses the middleware. """

    def test_response_has_id(self):
        response = self.client.get("/")
        self.assertTrue(response.has_header("X-Request-Id"))

    def test_response_id_is_used(self):
        response = self.client.get("/", {}, HTTP_X_REQUEST_ID="Fake")
        self.assertEqual(response.get("X-Request-Id"), "Fake")
