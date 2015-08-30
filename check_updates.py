# -*- coding: utf-8 -*-

import requests
from xml.etree import ElementTree
import logging
import os
import os.path

logging.basicConfig(level=logging.INFO)

url = 'http://www.currency-iso.org/dam/downloads/lists/list_one.xml'
response = requests.get(url)
if not response.ok:
    logging.error('Document %s not found, please check script' % url)
    exit(1)

data = ElementTree.fromstring(response.content)

remote_published = data.get('Pblshd')
try:
    with open(os.path.join('moneyed', 'add_currencies.py')) as f:
        local_published = f.readline()
        local_published = f.readline()[2:-1]
except IOError or FileNotFoundError:
    local_published = '1970-01-01'

if local_published >= remote_published:
    logging.info('Local file is up to date')
    exit(0)

logging.info('Begin parsing data...')
result = [
    '# -*- coding: utf-8 -*-',
    '# %s' % remote_published,
    'from .classes import add_currency',
    ''
]

currencies = dict()
for item in data.find('CcyTbl').findall('CcyNtry'):
    try:
        currency = item.find('Ccy').text
    except AttributeError:
        continue
    country = item.find('CtryNm').text
    if not currencies.get(currency):
        currencies[currency] = dict(countries=[country],
                                    currency=currency,
                                    numeric=item.find('CcyNbr').text,
                                    name=item.find('CcyNm').text,
                                    decimal_places=item.find('CcyMnrUnts').text)
    else:
        currencies[currency]['countries'].append(country)

    if currencies[currency]['decimal_places'] == 'N.A.':
        currencies[currency]['decimal_places'] = None

for currency, data in currencies.items():
    result.append((
       "%(currency)s = add_currency('%(currency)s', '%(numeric)s', '%(name)s',"
       " %(decimal_places)s, %(countries)s)") % data)

try:
    os.rename(os.path.join('moneyed', 'add_currencies.py'),
              os.path.join('moneyed', 'add_currencies_%s.py' % local_published))
except OSError or FileNotFoundError:
    pass
with open(os.path.join('moneyed', 'add_currencies.py'), 'w') as f:
    try: # Little hack to fit Python 2 and 3
        f.write('\n'.join(result).encode('utf-8'))
    except TypeError:
        f.write('\n'.join(result))
logging.info('Data parsed successfully, list of currencies was updated')