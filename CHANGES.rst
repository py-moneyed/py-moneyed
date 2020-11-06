============
 Change log
============

Significant or incompatible changes listed here.

Changes in development version (unreleased)
-------------------------------------------
* Dropped official support for Python 2.6, 3.2, 3.3, 3.4 (mainly because
  our test tools don't support them any more).

* Format ``Money`` instances using CLDR and Babel. This is a large change with lots of parts:

  * Added new ``moneyed.l10n`` module, containing a new ``format_money``
    function. This is a very thin wrapper around `babel.numbers.format_currency
    <http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency>`_
    and has all the same options. This allows us to get the official CLDR
    formats for currencies, in all the different locales.

    See docs in README.

    Note especially that you need to specify ``locale`` (e.g.
    ``locale="en_US"``), or you will get the ``LC_NUMERIC`` default.

  * Deprecated the ``format_money`` function in ``moneyed.localization``. There
    is no immediate plan to remove, but it should not be relied on. Also, this
    function relies on our own manually entered data for formatting of
    currencies in different locales. This data is very incomplete and will not
    be updated any more.

    So you need to use ``moneyed.l10n.format_money`` instead now.

    If you were relying on the ``decimal_places`` argument to the old function,
    there is no exact equivalent in the new ``format_money`` function, but see
    the ``decimal_quantization`` option (documented in
    `babel.numbers.format_currency
    <http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency>`_)

  * ``Money.__str__`` (``Money.__unicode__`` on Python 2) now uses new
    ``format_money`` with the default locale ``LC_NUMERIC``, which can produce
    different results from the old function. Use the new ``format_money`` to control
    output.

  * On Python 2, ``Money.__str__`` (bytestring) output has changed to be more
    basic. You should use the new ``format_money`` function to control output.

* Get currency names from Babel data. Several changes, including:

  * For all built-in currencies, ``Currency.name`` now comes from Babel ("en_US"
    locale). This means there have been various corrections to currency names.

    If you pass a non-None ``name`` to the ``Currency`` constructor, you can
    still specify any name you want.

  * ``Currency.get_name(locale)`` has been added.

* Get currency 'countries' from Babel data. Several changes, including:

  * ``Currency.countries`` now sources from Babel, so some names may be different.

  * ``Currency.country_codes`` has been added.

  * ``Currency.countries`` is deprecated, because it is not the most useful form
    for the data (e.g. upper cased strings, and names in US English only). It is
    recommended to use ``Currency.country_codes`` and convert to names using
    ``get_territory_name``.

Changes in v0.8
---------------

* ``Money.round([ndigits])`` added.
  Uses ``decimal.ROUND_HALF_EVEN`` by default, but this can be overridden
  by setting ``rounding`` in the ``decimal`` context before calling ``Money.round()``.
* Various fixes/additions for different locales
* Division support on Python 2
* DEFAULT locale is now used as a fallback to return a currency symbol if your
  chosen locale has no symbol set for that currency, rather than just returning
  the currency code.


Changes in v0.7
---------------

* Money.__str__ changed under Python 2 to use only ASCII characters.
  This means that currency codes, rather than symbols, are used.

* Lots of additional locales supported out of the box.

* Python 3.5 supported

* Fixed #70 - format_money error when the locale is not in the formatting
  definitions: the default is not used.

* Various other bug fixes


Changes in v0.6 and earlier
---------------------------

* See VCS logs.
