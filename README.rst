Overview
============================================================

The need to represent instances of money frequently arises in software
development, particularly any financial/economics software.  The
py-moneyed package provides the classes of Money and Currency to help
with that need, at a level more useful than just Python's Decimal
class, or ($DEITY forbid) the float primitive.  The package is meant
to be stand-alone and easy to either use directly, or subclass
further.  py-moneyed is BSD-licensed.

Some of the py-moneyed code was first derived from python-money
available via this URL: http://code.google.com/p/python-money/ Because
the Google Code version has been inactive since May 2008, I forked it
and modified it for my needs in 2010. Compared to python-money, major
changes in py-moneyed include separating it from Django usage,
tightening types handling in operators, a complete suite of unit
tests, PEP8 adherence, and providing a setup.py.


Usage
-----

On to the code: the Money class is instantiated with:

- An amount which can be of type string, float, or Decimal.
- A currency, which usually is specified by the  three-capital-letters
  ISO currency code,e.g. USD.

For example,

::

    from moneyed.classes import Money
    sale_price_today = Money(amount='99.99', currency='USD')

The Money class also provides operators with type checking, matching
currency checking, and sensible dimensional behavior, e.g. you cannot
multiply two Money instances, nor can you add a Money instance to a
non-Money number; dividing a Money instance by another results in a
Decimal value, etc.

The Currency class is provided with a complete dictionary of ISO 4217
currencies data, each key (e.g. 'USD') mapping to a Currency instance
with ISO numeric code, canonical name in English, and countries using
the currency.  Thanks to the python-money developers for their
(possibly tedious) data-entry of the ISO codes!


Testing
--------

Unit-tests have been provided, and can be run with py.test.  This
version has been tested with Python 2.6.  Should you use py-money with
other Python versions, please let me know if you are successful or
not.


Future
------

Future versions of py-moneyed may provide currency conversions, or
other capabilities, dependent on feedback and usage.
