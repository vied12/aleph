'''
Scripting for openoil tasks

'''

import pprint
from dateutil.parser import parse

from flask.ext.script import Manager

from aleph.core import es, es_index
from aleph.search.mapping import DOC_TYPE

from aleph.contrib.openoil import scheduled_updates

import aleph.core
import aleph.search


manager = Manager(usage="openoil admin tasks")

def replace_es(query, updatefunc, index='aleph_test'):
    results = es.search(index=index,body=query)
    for result in results['hits']['hits']:
        newbody = updatefunc(result['_source'])
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
    if filing_date:
        body['filed_at'] = filing_date.strftime('%Y%m%d')
    return body

@manager.command
def mungees():
    """
    Check status of ElasticSearch backend
    """
    # Get a test document
    query = {}
    replace_es(query, fix_date, index='aleph_dev')
    print('done')

@manager.command
def get_mappings():
    """
    Show the mappings of all ES indices
    """
    pprint.pprint(es.indices.get_mapping())
    
    
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
def rebuild_test_index():
    assert aleph.core.es_index == 'aleph_dev'
    aleph.search.delete_index()
    aleph.search.init_search()
    for i, result in enumerate(random_docs()):
        new = es.index(
            index='aleph_dev',
            doc_type = result['_type'],
            body = result['_source'],
            )
        assert new['created'] == True
    print('created %s docs' % i)
    
def random_docs():
    index = 'aleph'
    query = {
        "query": {
            "function_score": {
                "functions": [{
                    "random_score": {"seed": 42}}]
            }
        }
    }
    results = es.search(index=index,body=query)
    return results['hits']['hits']
    '''
    import pprint
    for r in results['hits']['hits']:
        pprint.pprint(r)
    '''
    
@manager.command
def schedule():
    """
    Run scrapers by schedule
    """
    scheduled_updates.schedule_updates()
