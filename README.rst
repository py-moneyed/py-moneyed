.. image:: https://github.com/limist/py-moneyed/workflows/build/badge.svg
    :target: https://github.com/limist/py-moneyed/actions?query=workflow%3Abuild
    :alt: Build Status

.. image:: https://badge.fury.io/py/py-moneyed.svg
    :target: https://badge.fury.io/py/py-moneyed
    :alt: Latest PyPI version

Overview
========

The need to represent instances of money frequently arises in software
development, particularly any financial/economics software.  To
address that need, the py-moneyed package provides the classes of
Money and Currency, at a level more useful than just using Python's
Decimal class, or ($DEITY forbid) the float primitive.  The package is
meant to be stand-alone and easy to either use directly, or subclass
further.  py-moneyed is BSD-licensed.

Some of the py-moneyed code was first derived from python-money
available via this URL: http://code.google.com/p/python-money/ Because
that Google Code version has been inactive since May 2008, I forked it
and modified it for my needs in 2010. Compared to python-money, major
changes here in py-moneyed include separating it from Django usage,
tightening types handling in operators, a complete suite of unit
tests, PEP8 adherence, providing a setup.py, and local currency
formatting/display.

Installation
------------
You can install using pip::

    pip install py-moneyed

Usage
-----

On to the code! The Money class is instantiated with:

- An amount which can be of type int, string, float, or Decimal.
  It will be converted to a Decimal internally. Therefore, it is best
  to avoid float objects, since they do not convert losslessly
  to Decimal.

- A currency, which usually is specified by the three-capital-letters
  ISO currency code, e.g. USD, EUR, CNY, and so on.
  It will be converted to a Currency object.

For example,

.. sourcecode:: python

    from moneyed import Money
    sale_price_today = Money(amount='99.99', currency='USD')


You then use Money instances as a normal number. The Money class provides
operators with type checking, matching currency checking, and sensible
dimensional behavior, e.g. you cannot multiply two Money instances, nor can you
add a Money instance to a non-Money number; dividing a Money instance by another
results in a Decimal value, etc.

The Currency class is provided with a complete dictionary of ISO 4217
currencies data, each key (e.g. 'USD') mapping to a Currency instance
with ISO numeric code, canonical name in English, and countries using
the currency.  Thanks to the python-money developers for their
(possibly tedious) data-entry of the ISO codes!

All of these are available as pre-built Currency objects in the `moneyed`
module.

You can also pass in the arguments to Money as positional arguments.
So you can also write:

.. sourcecode:: python

    >>> from moneyed import Money, USD
    >>> price = Money('19.50', USD)
    >>> price
    <Money: 19.50 USD>

    >>> price.amount
    Decimal('19.50')

    >>> price.currency
    USD

    >>> price.currency.code
    'USD'


Formatting
----------

You can print Money object as follows:

.. sourcecode:: python

   >>> from moneyed.l10n import format_money
   >>> format_money(Money(10, USD), locale='en_US')
   '$10.00'

Note that you need to specify ``locale`` or you will get the system default,
which will probably not be what you want. For this reason, it is recommended to
always provide the ``locale`` argument, and you may well want to add your own
wrappers around this function to supply your project specific defaults.

This function is a thin wrapper around `babel.numbers.format_currency
<http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency>`_.
See those docs for other arguments that can be specified to control the
formatting of the number. By default, Babel will apply definitions of how to
format currencies that have been derived from the large `CLDR database
<http://cldr.unicode.org/>`_.

If you do ``str()`` on a ``Money`` object (or ``unicode()`` in Python 2), you
will get the same behaviour as ``format_money()``, but with no options supplied,
so you will get the system default locale.

There is also a deprecated ``format_money`` function in
``moneyed.localization``, which has a different signature, and relied on our own
very incomplete lists of formats.

Division on Python 2 code
-------------------------

This package uses the special method `__truediv__` to add division support to
`Money` class. So, if you are using python 2, make sure that you have imported
division on your code that calls division operation, otherwise you will get
unsupported operand error.

.. sourcecode:: python

    >>> from __future__ import division
    >>> from moneyed import Money
    >>> price = Money(amount='50', currency='USD')
    >>> price / 2
    <Money: 25 USD>

Search by Country Code
----------------------

In order to find the ISO code associated with a country, the global
method `get_currencies_of_country` can be used. The function takes
the ISO country code (case insensitive) as the argument and returns the
associated currency object(s) in a list. If a country with the given
name is not found the function returns an empty list.
The code below demonstrates this:

.. sourcecode:: python

    >>> from moneyed import get_currencies_of_country
    >>> get_currencies_of_country("IN")
    [Currency(INR)]
    >>> get_currencies_of_country("TV")
    [Currency(AUD), Currency(TVD)]
    >>> get_currencies_of_country("XX")
    []


Testing
-------

Unit-tests have been provided, and can be run with tox_ (recommended)
or just py.test.

If you don't have tox installed on your system, it's a modern Python
tool to automate running tests and deployment; install it to your
Python environment with::

    pip install tox


Then run it from the source directory::

    tox

If you do not have all versions of Python that are used in testing,
you can use pyenv_. After installing pyenv, install the additional
plugin pyenv-implict_.

The py-moneyed package is tested against Python 2.7, 3.5 - 3.9
and PyPy 2 and 3

.. _tox: http://tox.testrun.org/latest/
.. _pyenv: https://github.com/yyuu/pyenv
.. _pyenv-implict: https://github.com/concordusapps/pyenv-implict

Future
------

Future versions of py-moneyed may provide currency conversions or
other capabilities, dependent on feedback and usage.
