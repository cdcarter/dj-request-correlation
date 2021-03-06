#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from dj_request_correlation/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version("dj_request_correlation", "__init__.py")


if sys.argv[-1] == "publish":
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    sys.exit()

if sys.argv[-1] == "tag":
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

README = open("README.md").read()
HISTORY = open("HISTORY.md").read()

setup(
    name="dj-request-correlation",
    version=version,
    description="""Django support for X-Request-Id and other request correlation techniques""",
    long_description=README + "\n\n" + HISTORY,
    author="Christian Carter",
    author_email="christian.carter@salesforce.com",
    url="https://github.com/cdcarter/dj-request-correlation",
    packages=["dj_request_correlation"],
    include_package_data=True,
    install_requires=["django"],
    license="MIT",
    zip_safe=False,
    keywords="dj-request-correlation",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
)
