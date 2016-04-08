from flask import Blueprint
from apikit import jsonify

from aleph.views import search_api


blueprint = Blueprint('public', __name__)

result_element_whitelist = (
    "archive_url","attributes", "collection", "id", "manifest_url",
    "name","redirect_url","score","source_url", "title","updated_at", "filed_at",
    )



def flatten_attributes(data):
    for result in data['results']:
        new_attribs = {}
        old_attribs = result.pop('attributes')
        for att in old_attribs:
            new_attribs[att['name']] = att['value']
            result['attributes'] = new_attribs
    return data

def result_filter(rs):
    newlist = []
    for result in rs:
        newr = {}
        for k,v in result.items():
            if k in result_element_whitelist:
                newr[k] = v
        newlist.append(newr)
    return newlist

def public_process(data):
    data = flatten_attributes(data)
    data.pop('facets')
    data['results'] = result_filter(data['results'])
    nd = {}
    return data

@blueprint.route('/aleph_api/1/query')
def query():
    data = search_api._query()
    data = search_api.preprocess_data(data)
    data = public_process(data)
    return jsonify(data)


