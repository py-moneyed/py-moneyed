============
 Change log
============

Significant or incompatible changes listed here.


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
