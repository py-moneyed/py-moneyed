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

Usage
-----

On to the code! The Money class is instantiated with:

- An amount which can be of type string, float, or Decimal.  
- A currency, which usually is specified by the three-capital-letters
  ISO currency code, e.g. USD, EUR, CNY, and so on.

For example,

.. sourcecode:: python

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

In order to find the ISO code associated with a country, the global
method 'get_currency_of_country' can be used. The function takes
the country name (case insensitive) as the argument and returns the
associated currency object(s) in a list. If a country with the given
name is not found the function returns 'None'.
The code below demonstrates this:

.. sourcecode:: python
				from moneyed.classes import get_currency_of_country
				get_currency_of_country("India") # Returns INR object in a list
				get_currency_of_country("Tuvalu") # Returns AUD, TVD objects in a list
				get_currency_of_country("Oompaland") # Returns 'None'

Testing
-------

Unit-tests have been provided, and can be run with tox_ (recommended)
or just py.test.

If you don't have tox installed on your system, it's a modern Python
tool to automate running tests and deployment; install it to your
global Python environment with: ::

    sudo pip install tox
    
Then you can activate a virtualenv (any will do - by design tox will
not run from your globally-installed python), cd to the py-moneyed
source directory then run the tests at the shell: ::

    cd where/py-moneyed-source/is
    tox

If you do not have all versions of Python that are used in testing,
you can use pyenv_. After installing pyenv, install the additional
plugin pyenv-implict_.

The py-moneyed package has been tested with Python 2.6, 2.7, 3.2, 3.3 
and PyPy 2.1.

.. _tox: http://tox.testrun.org/latest/
.. _pyenv: https://github.com/yyuu/pyenv
.. _pyenv-implict: https://github.com/concordusapps/pyenv-implict

Future
------

Future versions of py-moneyed may provide currency conversions or
other capabilities, dependent on feedback and usage.

