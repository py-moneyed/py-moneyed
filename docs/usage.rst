Usage
=====

.. currentmodule:: moneyed

The :class:`Money` class is instantiated with:

- An amount which can be of type int, string, float, or Decimal. It will be
  converted to a Decimal internally. Therefore, it is best to avoid float
  objects, since they do not convert losslessly to Decimal.

- A currency, as a :class:`Currency` object, or as a string which is a
  three-capital-letters ISO currency code (e.g. ``'USD'``, ``'EUR'`` etc), which
  will be converted to a :class:`Currency` object.

For example,

.. code-block:: python

    from moneyed import Money
    sale_price_today = Money(amount='99.99', currency='USD')


You then use :class:`Money` instances as a normal number. The Money class provides
operators with type checking, matching currency checking, and sensible
dimensional behavior, e.g. you cannot multiply two Money instances, nor can you
add a Money instance to a non-Money number; dividing a Money instance by another
results in a Decimal value, etc.

The :class:`Currency` class is also provided. All ISO 4217 currencies are
available by importing from the ``moneyed`` module by their 3-letter code, as
pre-built :class:`Currency` objects.

You can also pass in the arguments to :class:`Money` as positional arguments. So
you can also write:

.. code-block:: python

    >>> from moneyed import Money, USD
    >>> price = Money('19.50', USD)
    >>> price
    Money('19.50', 'USD')

    >>> price.amount
    Decimal('19.50')

    >>> price.currency
    USD

    >>> price.currency.code
    'USD'


If you want to get the amount in sub units (ISO 4127 compatible) you can do:

.. code-block:: python

    >>> from moneyed import Money, USD
    >>> price = Money('19.50', USD)
    >>> price.get_amount_in_sub_unit()
    1950

    >>> price = Money('123.456', USD)
    >>> price.get_amount_in_sub_unit()
    12345


Currency instances have a ``zero`` property for convenience. It returns a cached
``Money`` instance of the currency. This can be helpful for instance when summing up a
list of money instances using the builtin ``sum()``.

.. code-block:: python

    >>> from moneyed import Money, USD
    >>> currency = USD
    >>> items = (Money('19.99', currency), Money('25.00', currency))

    >>> sum(items, currency.zero)
    Money('44.99', 'USD')

    >>> sum((), currency.zero)
    Money('0', 'USD')


Search by Country Code
----------------------

In order to find the ISO code associated with a country, the function
:func:`get_currencies_of_country` can be used. This function takes the ISO
country code (case insensitive) as the argument and returns the associated
currency object(s) in a list. If a country with the given name is not found the
function returns an empty list. The code below demonstrates this:

.. code-block:: python

    >>> from moneyed import get_currencies_of_country
    >>> get_currencies_of_country("IN")
    [INR]
    >>> get_currencies_of_country("BO")
    [BOB, BOV]
    >>> get_currencies_of_country("XX")
    []

Get country names
-----------------

``Currency.country_codes`` returns a list of `ISO 3166 country codes
<https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes>`_. You can
convert these to names using the function ``get_country_name``, which must be
passed a ISO 2-letter code and a locale code:

.. code-block:: python

   >>> from moneyed import ZMW, get_country_name
   >>> ZMW.country_codes
   ['ZM']
   >>> get_country_name('ZM', 'en')
   'Zambia'

List all currencies
-------------------

You can get all installed currencies as below:

.. code-block:: python

   >>> from moneyed import list_all_currencies
   >>> list_all_currencies()
   [ADP, AED, AFA, ...]

The result is a list of :class:`Currency` objects, sorted by ISO code.
