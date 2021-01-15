.. image:: https://github.com/py-moneyed/py-moneyed/workflows/build/badge.svg
    :target: https://github.com/py-moneyed/py-moneyed/actions?query=workflow%3Abuild
    :alt: Build Status

.. image:: https://badge.fury.io/py/py-moneyed.svg
    :target: https://pypi.org/project/py-moneyed/
    :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/py-moneyed/badge/?version=latest
   :target: http://py-moneyed.readthedocs.io/en/latest/?badge=latest

Overview
========

The need to represent instances of money frequently arises in software
development, particularly any financial/economics software. To address that
need, the py-moneyed package provides the classes of Money and Currency, at a
level more useful than just using Python's Decimal class, or ($DEITY forbid) the
float primitive. The package is meant to be stand-alone and used directly, or
be subclassed further. py-moneyed is BSD-licensed.

Quick start
-----------

To install::

    pip install py-moneyed

Use:

.. sourcecode:: python

    from moneyed import Money, USD

    five_dollars = Money(5, USD)

You then use ``Money`` objects as if they were numbers, and they behave
sensibly. See `docs <https://py-moneyed.readthedocs.io/en/latest/>`_ for more
information (or the ``docs/`` folder).

History
-------

Some of the py-moneyed code was first derived from python-money
available via this URL: http://code.google.com/p/python-money/
Due to inactivity, it was forked by @limist in 2010 and later
moved to the py-moneyed organization.
