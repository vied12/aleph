'''
Scripting for openoil tasks
'''

import pprint
from dateutil.parser import parse

from flask.ext.script import Manager

from aleph.core import es, es_index
from aleph.search.mapping import DOC_TYPE
from aleph.search.attributes import generate_attributes

from aleph.contrib.openoil import scheduled_updates

from oocrawlers import sedar

import aleph.core
import aleph.search


manager = Manager(usage="openoil admin tasks")

def replace_es(query, updatefunc, index='aleph_test', howmany=10):
    perpage = 500
    for offset in range(0,howmany,perpage):
        results = es.search(
            index=index,
            body=query,
            from_=offset,
            size=min(perpage, howmany))
        for result in results['hits']['hits']:
            newbody = updatefunc(result['_source'])
            if not newbody:
                print('skipping item')
                continue
            updated = es.index(
                index=result['_index'],
                doc_type=result['_type'],
                id = result['_id'],
                body = newbody)
            assert updated['created'] == False

def sample_res_func(body):
    body['test_filed_at'] = "20120130"
    return body

def guess_filing_date(body):
    for ad in body['attributes']:
        for key in ('filing_date', 'Filing Date', 'date', 'filingDate', 'announcement_date'):
            if ad['name'] == key:
                try:
                    return parse(ad['value'])
                except (ValueError):
                    continue
    return None

def fix_date(body):
    filing_date = guess_filing_date(body)
    print('guessed filing date for %s as %s' % (body['collection'], filing_date.strftime('%Y%m%d') if filing_date else '[None]'))
    if filing_date:
        body['filed_at'] = filing_date.strftime('%Y%m%d')
    elif body['collection'] not in (
            'rigzone', 'lse', 'sedar-partial-content',
            'johannesburg-exchange', 'eiti'):
        import ipdb; ipdb.set_trace()
    return body

@manager.command
def fixsedar(n=10):
    def _inner(body):
        metadata = sedar.collect_sedar_metadata(body['source_url'])
        if len(body['attributes']) > 0:
            return None
        attributes = generate_attributes(metadata)
        body['attributes'] = attributes
        body = fix_date(body)
        return body
    n=int(n)
    query = {'query': {
        'term': {'collection': 'sedar-partial-content'}}
             }
    replace_es(query, _inner, index='aleph_dev', howmany=n)

@manager.command
def mungees(n=10):
    """
    Check status of ElasticSearch backend
    -n for number of docs to look at
    """
    n = int(n)
    query = {}
    replace_es(query, fix_date, index='aleph_dev', howmany=n)
    print('done')

@manager.command
def get_mappings():
    """
    Show the mappings of all ES indices
    """
    pprint.pprint(es.indices.get_mapping())

@manager.command
def console():
    query = {'query': {
        'term': {'collection': 'sedar-partial-content'}}
             }
    res = es.search(body=query,index='aleph_dev')
    import ipdb; ipdb.set_trace()
    
@manager.command
def add_date_mapping():
    assert es_index == 'aleph_dev'
    newfield = {"properties":
                {
                    "filed_at": {
                        "type": "date",
                        "format": "basic_date", #YYYYMMdd
                    },
                },
        }
    es.indices.put_mapping(
        index = es_index,
        doc_type = DOC_TYPE,
        body = newfield)
    
                    
    
@manager.command
def rebuild_test_index(n=100):
    n=int(n)
    assert aleph.core.es_index == 'aleph_dev'
    aleph.search.delete_index()
    aleph.search.init_search()
    docswanted=n
    perpage = 10
    for offset in range(0,docswanted,perpage):
        for i, result in enumerate(random_docs(howmany=perpage,offset=offset)):
            new = es.index(
                index='aleph_dev',
                doc_type = result['_type'],
                body = result['_source'],
            )
            assert new['created'] == True
    print('created %s docs' % i)
    
def random_docs(howmany=100, offset=0):
    index = 'aleph'
    query = {
        "from": offset,
        "size": howmany,
        "query": {
            "function_score": {
                "functions": [{
                    "random_score": {"seed": 42}}]
            }
        }
    }
    results = es.search(index=index,body=query)
    return results['hits']['hits']
    
@manager.command
def schedule():
    """
    Run scrapers by schedule
    """
    scheduled_updates.schedule_updates()
