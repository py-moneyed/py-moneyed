import re

from babel import Locale
from babel.core import get_global, default_locale

from .constants import (
    OBSELETE_CURRENCIES,
    COMMON_ISO_CODES,
    OBSELETE_ISO_CODES,
    XCOMMON_ISO_CODES,
)
from .money import add_currency

DEFAULT_LOCALE = default_locale('LC_ALL')

# This regex is used to find obselete currencies not in list
CONTAINS_YEAR_REGEX = re.compile('.*([1-3][0-9]{3})')


def _find_country_names_by_code(country_codes, locale, force_upper=False):
    countries = []
    for country_code in country_codes:
        country = locale.territories.get(country_code)
        if country is not None:
            if force_upper:
                country = country.upper()
            countries += [country]
    return countries


def get_iso_code(currency_code):
    if currency_code in COMMON_ISO_CODES:
        return COMMON_ISO_CODES[currency_code]

    if currency_code in XCOMMON_ISO_CODES:
        return XCOMMON_ISO_CODES[currency_code]

    if currency_code in OBSELETE_ISO_CODES:
        return OBSELETE_ISO_CODES[currency_code]
    return 'Nil'


def load_currencies(
    currency_list=None,
    load_x_currencies=True,
    load_obselete_currencies=False,
    load_iso_currency_codes=True,
    locale=DEFAULT_LOCALE,
):
    # get all currencies from babel, if currency_list not provided
    if currency_list is None:
        currency_list = get_global('all_currencies').keys()
    else:
        load_x_currencies = True
        load_obselete_currencies = True

    locale = Locale.parse(locale)

    for currency in currency_list:
        name = locale.currencies[currency]
        if not load_obselete_currencies:
            if currency in OBSELETE_CURRENCIES:
                continue
            if re.match(CONTAINS_YEAR_REGEX, name):
                continue

        if not load_x_currencies and currency in XCOMMON_ISO_CODES:
            continue

        if not load_iso_currency_codes:
            currency_code = 'Nil'
        else:
            currency_code = get_iso_code(currency)

        country_codes = get_global('all_currencies')[currency]
        countries = _find_country_names_by_code(
            country_codes, locale=locale, force_upper=True
        )
        add_currency(currency, currency_code, name, countries)
