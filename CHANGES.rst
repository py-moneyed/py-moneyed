============
 Change log
============

Significant or incompatible changes listed here.

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
