============
 Change log
============

Significant or incompatible changes listed here.

Unreleased - TBA
----------------
* Dropped support for Python 2.7 and 3.5 and PyPy 2.
* Added pyupgrade pre-commit hook.
* Added black pre-commit hook and reformatted codebase.
* Updated pre-commit hooks.
* Replaced custom flake8, isort and check-manifest Github Action jobs with a generic
  pre-commit job.
* Dropped the ``moneyed.localization`` module that was deprecated and announced for
  removal in 1.0.
* Added type hints along with a mypy pre-commit hook.
* Added action for building and publishing releases, along with the
  check-github-workflows pre-commit hook for validating Github Action workflow files.
* Removed undocumented ``DEFAULT_CURRENCY`` and ``DEFAULT_CURRENCY_CODE`` constants, and
  change to make instantiating ``Money`` without providing a currency a type error. This
  used to result in an object with a made-up ``"XYZ"`` currency, which could lead to
  surprising behaviors and bugs.
* Added ``zero`` property to ``Currency`` to conveniently access the zero value of a
  given currency.

1.2 (2020-02-23)
----------------
* ``Money.__add__`` returns ``NotImplemented`` instead of raising an exception when another operand has unsupported type.

1.1 (2020-01-15)
----------------
* Changed the ``numeric`` attribute values to ``None`` for currencies that don't have assigned ISO numeric codes: ``IMP``, ``TVD``, ``XFO``, ``XFU``.
* Restored the previous definition for the ``XXX`` currency, including its ``name`` and ``countries`` attributes.
* Fixed ``get_currency`` returning obsolete currencies.

1.0 (2020-01-09)
----------------
* Dropped official support for Python 2.6, 3.2, 3.3, 3.4 (mainly because
  our test tools don't support them any more).

* Added support for getting amount in sub units (fixed point)

* Format ``Money`` instances using CLDR and Babel. This is a large change with lots of parts.
  Many thanks to @pooyamb for all the hard work that went into this and other
  related changes.

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
    ``get_country_name``.

* Changed the repr of ``Money`` so that ``eval(repr(money_object) ==
  money_object`` (at least in some environments, and most of the typical ones).
  See `Python docs on __repr__
  <https://docs.python.org/3/reference/datamodel.html?highlight=__repr__#object.__repr__>`_
  for rationale. Thanks `@davidtvs <https://github.com/davidtvs>`_. This could
  be backwards incompatible if you were relying on the old output of ``repr()``.

* Added ``list_all_currencies()`` utility function.

0.8 (2018-11-19)
----------------

* ``Money.round([ndigits])`` added.
  Uses ``decimal.ROUND_HALF_EVEN`` by default, but this can be overridden
  by setting ``rounding`` in the ``decimal`` context before calling ``Money.round()``.
* Various fixes/additions for different locales
* Division support on Python 2
* DEFAULT locale is now used as a fallback to return a currency symbol if your
  chosen locale has no symbol set for that currency, rather than just returning
  the currency code.


0.7 (2017-05-08)
----------------

* ``Money.__str__`` changed under Python 2 to use only ASCII characters.
  This means that currency codes, rather than symbols, are used.

* Lots of additional locales supported out of the box.

* Python 3.5 supported

* Fixed #70 - format_money error when the locale is not in the formatting
  definitions: the default is not used.

* Various other bug fixes


0.6 and earlier
---------------

* See VCS logs.
