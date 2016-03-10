import re
from six.moves import urllib
import google_measurement_protocol
from flask import Blueprint
blueprint = Blueprint('search', __name__)
from aleph.search import search_documents

def find_original_url(doc):
    '''
    Various hacks to figure out the original source url of
    collections that were not properly curated to begin with
    '''
    if doc['collection'] == 'lse' and 'data.openoil.net' in doc.get('source_url', ''):
        try:
            docid = re.search('(\d+).html', doc['source_url']).group(1)
            return 'http://www.londonstockexchange.com/exchange/news/market-news/market-news-detail/%s.html' % docid
        except Exception:
            pass
    if doc['collection'] == 'edgar-partial-content':
        try:
            pass
        except Exception:
            pass
    return doc.get('url', doc.get('source_url', ''))


def preprocess_data(data):
    ordered_attribs = [
	  ['Company Name', ['Company Name', 'company_name', 'companyName', 'sedar_company_id', 'Company name', 'companyCode', 'company']],
	  ['Industry Sector', ['Industry Sector', 'industry', 'assignedSIC', 'sector_name']],
	  ['Filing Type', ['Filing Type', 'filing_type', 'file_type', 'document_type']],
	  ['Filing Date', ['Filing Date', 'date', 'filingDate', 'announcement_date']],	   
	   ]    
    for result in data['results']:
        result['attribs_to_show'] = []
        for human_name, db_names in ordered_attribs:
            for attribute in result['attributes']:
                if attribute['name'] in db_names:
                    result['attribs_to_show'].append([human_name, attribute['value']])
                    result['top_attribs'], result['bottom_attribs'] = result['attribs_to_show'][:2], result['attribs_to_show'][2:]
                    break
        original_url = find_original_url(result) or ''
        print(original_url)
        result['redirect_url'] = "https://search.openoil.net/api/1/exit?u=%s" % urllib.parse.quote(original_url.encode('utf8'))

    return data

@blueprint.route('/api/1/exit')
def exit_redirect():
    '''
    Track clicks on external links, mainly for the benefit
    of google analytics
    '''
    rawurl = request.args.get('u', 'https://search.openoil.net')
    newurl = urllib.parse.unquote(rawurl)
    # XXX tracking happens here, right?
    user_id = request.cookies.get('oo_search_user', 'unknown user')
    ua = app.config.get('GOOGLE_ANALYTICS_UA')
    view = google_measurement_protocol.PageView(
        path=request.url, referrer = request.referrer)
    google_measurement_protocol.report(
        ua, user_id, view)
    return redirect(newurl)

def docs_this_week():
    '''
    Return how many documents have been added
    to the index this week
    '''
    query = {'query': {'range': {'created_at': {'gte': 'now-7d/d'}}}}
    res = search_documents(query)
    return res.result['hits']['total']
