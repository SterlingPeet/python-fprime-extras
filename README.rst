========
Overview
========

WARNING:  This branch and release is just a template.  See the ``devel`` branch for preview code.

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-fprime-extras/badge/?style=flat
    :target: https://readthedocs.org/projects/python-fprime-extras
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/SterlingPeet/python-fprime-extras.svg?branch=main
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/SterlingPeet/python-fprime-extras

.. |requires| image:: https://requires.io/github/SterlingPeet/python-fprime-extras/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/SterlingPeet/python-fprime-extras/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/SterlingPeet/python-fprime-extras/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/SterlingPeet/python-fprime-extras

.. |version| image:: https://img.shields.io/pypi/v/fprime-extras.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/fprime-extras

.. |wheel| image:: https://img.shields.io/pypi/wheel/fprime-extras.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/fprime-extras

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/fprime-extras.svg
    :alt: Supported versions
    :target: https://pypi.org/project/fprime-extras

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/fprime-extras.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/fprime-extras

.. |commits-since| image:: https://img.shields.io/github/commits-since/SterlingPeet/python-fprime-extras/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/SterlingPeet/python-fprime-extras/compare/v0.0.0...main



.. end-badges

Extra tools for working with F Prime projects.

* Free software: MIT license

Installation
============

::

    pip install fprime-extras

You can also install the in-development version with::

    pip install https://github.com/SterlingPeet/python-fprime-extras/archive/main.zip


Documentation
=============


https://python-fprime-extras.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
