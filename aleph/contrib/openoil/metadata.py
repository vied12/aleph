'''
Fixes for various metadata issues
'''

import re

from dateutil.parser import parse
from dateutil import tz
import datetime


date_string_format = '%Y%m%d' # must match elasticsearch date format requirements

sa_date_format = re.compile(r'''
        # should match Date(1405954279357+0200)
Date    # string Date
\(      # open parentheses
(\d+)   # milliseconds since the epoch
(
[\+-]   # + or -
\d+     # timezone offset
)
\)      # close parentheses
''', re.VERBOSE)

def guess_filing_date_sa(val):
    assert sa_date_format.match(val)
    milliseconds, timezone = sa_date_format.match(val).groups()
    offset = tz.tzoffset('UTC', int(timezone) / 100 * 60 * 60)
    dt = datetime.datetime.fromtimestamp(int(milliseconds)/1000, offset)
    return dt

def guess_filing_date(body):
    for ad in body['attributes']:
        for key in ('filing_date', 'Filing Date', 'date', 'filingDate', 'announcement_date'):
            if ad['name'] == key:
                if sa_date_format.match(ad['value']):
                    return guess_filing_date_sa(ad['value'])
                try:
                    return parse(ad['value'])
                except (ValueError):
                    continue
    return None

def fix_date(body):
    filing_date = guess_filing_date(body)
    print('guessed filing date for %s as %s' % (body['collection'], filing_date.strftime(date_string_format) if filing_date else '[None]'))
    if filing_date:
        body['filed_at'] = filing_date.strftime('%Y%m%d')
    elif body['collection'] not in (
            'rigzone', 'lse', 'sedar-partial-content',
            'johannesburg-exchange', 'eiti'):
        import ipdb; ipdb.set_trace()
    return body
