# Aleph Search API

## Introduction

The Aleph API enables you to search for corporate filings from extractives companies

## Endpoints

The api is available at https://search.openoil.net/aleph_api/1/

Currently the only supported request is searching through documents, at

https://search.openoil.net/aleph_api/1/query

## Request Format

The following parameters are available:

 - q -- search terms, using the elasticsearch-based syntax described
at http://search.openoil.net/help
 - offset, limit -- for paging of results
 - source -- which document bases to include

## Result format

The API will return a JSON dictionary. The most important item wihin it is 'results'. This contains a list of matches, each of which is a dictionary with the following items:

- archive_url: a link to our cached copy of the document
- collection: which of our document bases the document is from
- source_url: original source (e.g. on the regulator website). 
- title: document title. No
- score: how well the document matches the search query, as measured by elasticsearch
- updated_at: when Aleph downloaded the document

## Example

TODO

## Python example

TODO
