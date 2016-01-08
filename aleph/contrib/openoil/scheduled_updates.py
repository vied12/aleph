'''
Update sources on a schedule
'''
import schedule
import time, datetime
from aleph.crawlers import crawl_source


def _crawler(sourcename):
    def _inner():
        crawl_source(sourcename, ignore_tags=False)
    return _inner
    
def schedule_updates():
    schedule.every(3).days.do(_crawler('sec-edgar'))

    while(1):
        schedule.run_pending()
        time.sleep(1)
    
