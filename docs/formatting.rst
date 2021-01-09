Formatting
==========

You can print :class:`Money` object as follows:

.. code-block:: python

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
