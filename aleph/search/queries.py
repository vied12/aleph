from copy import deepcopy
import logging
import re

from werkzeug.datastructures import MultiDict

DEFAULT_FIELDS = ['title', 'name', 'extension', 'collection',
                  'id', 'updated_at', 'slug', 'source_url', 'source',
                  'summary', 'attributes']

QUERY_FIELDS = ['title', 'source_url', 'summary', 'extension', 'mime_type',
                'text', 'entities.label', 'attributes.value']


def add_filter(q, flt):
    if 'filtered' not in q:
        return {
            'filtered': {
                'query': q,
                'filter': flt
            }
        }

    if 'and' in q['filtered']['filter']:
        q['filtered']['filter']['and'].append(flt)
    else:
        q['filtered']['filter'] = \
            {'and': [flt, q['filtered']['filter']]}
    return q


def get_list_facets(args):
    for list_id in args.getlist('listfacet'):
        try:
            yield int(list_id)
        except:
            pass

def _add_date_filter(filtered_q, args, newerthan):
    if newerthan is None:
        return filtered_q
    cf = {'range': {'updated_at': {"gte": newerthan}}}
    filtered_q = add_filter(filtered_q, cf)
    return filtered_q

def document_query(args, fields=DEFAULT_FIELDS, sources=None, lists=None,
                   facets=True, highlights=False, newerthan=None):
    if not isinstance(args, MultiDict):
        args = MultiDict(args)

    filtered_q = _build_qstr_query(args)
    filtered_q = _add_entities_filter(filtered_q, args)
    filtered_q = _add_attribute_filter(filtered_q, args)
    filtered_q = _add_collections_filter(filtered_q, args, sources)
    filtered_q = _add_date_filter(filtered_q, args, newerthan)
    aggs = _make_aggregations(facets, filtered_q, args, lists)

    q = apply_sorting(filtered_q, args, aggs, fields)

    if highlights:
        q['highlight'] = _make_highlights(fields)

    return q

def apply_sorting(q, args, aggs, fields):
    '''
    Ordering is specified by the 'sort' query parameter. Possible values are:

    1) 'raw' -- Raw lucene score
    Appropriate if you want to completely ignore recentness

    2) 'best' -- Lucene score, with date-based weighting (DEFAULT)
    This uses ES/Lucene's 'function_score', and combines the relevance
    score with a boost for more recent documents

    3) 'date' -- pure date-based weighting
    Using a plain sort, we ignore everything except the updated_at date

    NB both date orderings updated_at rather than filing date. This
    is because the filing date is not (currently) formatted as a date.
    '''
    
    if args.get('sort', None) == 'date':
        q = {
            'query': q,
            #'query': weighted_q,
            'aggregations': aggs,
            '_source': fields
        }
        q['sort'] = [
            { "filed_at": {"order": "desc"}},
            ]
    elif args.get('sort', None) == 'relevance':
        q = {
            'query': q,
            'aggregations': aggs,
            '_source': fields
        }
    else:
        weighted_q = _wrap_weighting(q)
        q = {
            #'query': filtered_q,
            'query': weighted_q,
            'aggregations': aggs,
            '_source': fields
        }
    return q

def _wrap_weighting(q):
    '''
    We want to weight documents higher based on date
    To do this, we use ES's 'funtion_score' feature
    as described at https://www.elastic.co/guide/en/elasticsearch/guide/current/boosting-by-popularity.html
    '''
    wrapped_q = {
        'function_score': {
            'query': q,
               'functions': [

                   # give extra weight to documents from our contracts collection
                   {'filter': {'term': {'collection': 'openoil-contracts'}},
                    'weight': 2},

                   # give extra weight to more recent documents
                   {'exp': {
                       'updated_at': {'scale': '10w'}
                   }},

                ],
        }
        }
    return wrapped_q


def _build_regex_query(args, fields=QUERY_FIELDS):
    qstr = args.get('q', '').strip()
    qstr = qstr.replace('regex:', '')
    logging.info('building regex query')
    logging.info(fields)
    logging.debug('qstr is %s' % qstr)
    query =  {
        "regexp": {
            "text": qstr,
            #"fields": ["title", "text"],
            #"analyze_wildcard": True,
            }
        }
    '''multi_query = {
        "bool": {
            "should": [
                {"regexp": {
                    "text": {
                        "value": qstr,
                        "flags": "NONE",
                    }
                 }},
                #{"regexp": {
                #    "title": qstr,
                #}},
            ]
        }
    }
    '''
    return query

def _partial_regex(querypart):
    querypart = querypart.replace('regex:', '')
    return {
        "regexp": {
            "text": querypart,
            #"fields": ["title", "text"],
            #"analyze_wildcard": True,
            }
        }




def _build_qstr_query(args):
    qstr = args.get('q', '').strip()
    if len(qstr):
        filtered_q = {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": qstr,
                            "fields": QUERY_FIELDS,
                            }
                    },

                ],
                
                #"should": [
                #    {
                #    "multi_match": {
                #        "query": qstr,
                #        "fields": QUERY_FIELDS,
                #        "type": "phrase"
                #    },
                #},
                #               
                #           ]
            }
        }
    else:
        filtered_q = {'match_all': {}}
    return filtered_q


def _add_entities_filter(filtered_q, args):
    # entities filter
    for entity in args.getlist('entity'):
        cf = {'term': {'entities.id': entity}}
        filtered_q = add_filter(filtered_q, cf)
    return filtered_q

def _add_attribute_filter(filtered_q, args):
    for key, value in args.items():
        if not key.startswith('attribute-'):
            continue
        _, attr = key.split('attribute-', 1)
        af = {
            "nested": {
                "path": "attributes",
                "query": {
                    "bool": {
                        
                        "must": [
                            {"term": {"attributes.name": attr}},
                            {"term": {"attributes.value": value}}
                        ]
                    }
                }
            }
        }
        filtered_q = add_filter(filtered_q, af)
    return filtered_q
        
def _add_collections_filter(filtered_q, args, sources):
    q = deepcopy(filtered_q)

    # collections filter
    if sources is not None:
        srcs = args.getlist('source') or sources
        srcs = [c for c in srcs if c in sources]
        if not len(srcs):
            srcs = ['none']
        cf = {'terms': {'collection': srcs}}
        q = add_filter(q, cf)

        all_coll_f = {'terms': {'collection': sources}}
        filtered_q = add_filter(filtered_q, all_coll_f)
    return q


def _make_highlights(fields):
    # XXX this should also include other fields
    highlights = {'fields': {}}
    for field in fields:
        highlights['fields'][field] = {
            "number_of_fragments": 99}
    return highlights

def _make_aggregations(facets, filtered_q, args, lists):
        
    aggs = {}    

    # query facets
    if facets:
        aggs = {
            'all': {
                'global': {},
                'aggs': {
                    'ftr': {
                        'filter': {'query': filtered_q},
                        'aggs': {
                            'collections': {
                                'terms': {'field': 'collection',
                                          'size': 1000,}
                            }
                        }
                    }
                }
            }
        }

        for list_id in get_list_facets(args):
            if list_id not in lists:
                continue

            list_facet = {
                'nested': {
                    'path': 'entities'
                },
                'aggs': {
                    'inner': {
                        'filter': {'term': {'entities.list': list_id}},
                        'aggs': {
                            'entities': {
                                'terms': {'field': 'entity',
                                          'size': 50}
                            }
                        }
                    }
                }
            }
            aggs['list_%s' % list_id] = list_facet

        for attr in args.getlist('attributefacet'):
            attr_facet = {
                'nested': {
                    'path': 'attributes'
                },
                'aggs': {
                    'inner': {
                        'filter': {'term': {'attributes.name': attr}},
                        'aggs': {
                            'values': {
                                'terms': {'field': 'value',
                                          'size': 50}
                            }
                        }
                    }
                }
            }
            aggs['attr_%s' % attr] = attr_facet
    return aggs





def entity_query(selectors):
    texts = []
    for selector in selectors:
        if hasattr(selector, 'normalized'):
            selector = selector.normalized
        texts.append(selector)
    q = {
        'query': {'terms': {'normalized': texts}},
        '_source': ['collection', 'id']
    }
    return q


def attributes_query(args, sources=None, lists=None):
    q = document_query(args, sources=sources, lists=lists,
                       facets=False)
    q['aggregations'] = {
        'attributes': {
            'terms': {'field': 'attributes.name',
                      'size': 200}
        }
    }
    q['size'] = 0
    return q
