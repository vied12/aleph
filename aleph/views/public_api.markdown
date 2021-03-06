# Aleph Search API

## Introduction

The Aleph API enables you to search for corporate filings from extractives companies

## Endpoints

The api is available at https://search.openoil.net/aleph_api/1/

Currently the only supported request is searching through documents, at

https://search.openoil.net/aleph_api/1/query

## Authentication

To use the API, you need an openoil API key. You can obtain a key at https://openoil.net/openoil-api/

You should include this as in all API requests.

## Request Format

The following parameters are available:

 - apikey -- your OpenOil API key (oo_xxxxxxxxxxxxxxxx), obtained from https://openoil.net/openoil-api
 - q -- search terms, using the elasticsearch-based syntax described
at https://search.openoil.net/help
 - offset, limit -- for paging of results
 - source -- which document bases to include

## Result format

The API will return a JSON dictionary. The most important item wihin it is 'results'. This contains a list of matches, each of which is a dictionary with the following items:

- archive_url: a link to our cached copy of the document
- collection: which of our document bases the document is from
- source_url: original source (e.g. on the regulator website). 
- title: document title
- score: how well the document matches the search query, as measured by elasticsearch
- updated_at: when Aleph downloaded the document


## Python example

Using python, we can get a list of documents from Australian-listed companies talking about out-of-court settlements:

```python
import requests

req = requests.get(
    'https://search.openoil.net/aleph_api/1/query',
    params={
        'q': '"settled out of court"',
        'source': 'asx',
        'apikey': 'oo_xxxxxxxxx', # your key here!
        })

for result in req.json()['results']:
    print(result['title'])

```

Output is:

```

OIL BASINS LIMITED (2015-03-27): Settlement of Magistrates Court Legal Action
OIL BASINS LIMITED (2015-04-30): March 2015 Quarterly Activities Report
ROYAL RESOURCES (2012-07-30): Fourth Quarter Activities and Cashflow Report
MINDAX LIMITED (2013-02-27): Half Year Financial Report 31 December 2012
THUNDELARRA LTD (2006-12-28): Annual Report
GRAND GULF ENERGY (2013-09-26): Full Year Statutory Accounts
WINDIMURRA VANADIUM (2005-09-30): Full Year Accounts
IRONCLAD MINING (2009-10-01): Full Year Statutory Accounts
ROYAL RESOURCES (2012-10-22): Annual Report 2012
JAMES HARDIE INDUST (2007-05-28): KPMG Actuaries Valuation Report
IRONCLAD MINING (2010-10-01): Annual Report to shareholders
JAMES HARDIE INDUST (2008-05-22): KPMG Report - 31 March 2008

```


The URL we are requesting here is https://search.openoil.net/aleph_api/1/query?q=%22settled+out+of+court%22&source=asx&apikey=oo_xxxxxxxxxxxxxxx
