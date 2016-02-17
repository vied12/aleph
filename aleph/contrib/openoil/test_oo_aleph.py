from aleph.contrib.openoil import metadata


def test_filing_date():
    dates = (
        ('2014-01-01', '20140101'),
        ('Date(1405954279357+0200)', '20140721'),
        )
    for orig, result in dates:
        body = {
            'attributes': [{'name': 'Filing Date',
                            'id': 'n/a',
                            'value': orig,
                            },]
             }
        parsed = metadata.guess_filing_date(body)
        stringoutput = parsed.strftime(metadata.date_string_format)
        assert result == stringoutput


def test_sa_date():
    raw, expected = ('Date(1405954279357+0200)', '20140721')
    assert metadata.sa_date_format.match(raw)
    actual_datetime = metadata.guess_filing_date_sa(raw)
    actual = actual_datetime.strftime(metadata.date_string_format)
    assert actual == expected
