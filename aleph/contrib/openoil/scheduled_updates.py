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
    intervals = (
        (3, 'sec-edgar'),
        (1, 'sedar-partial-content'),
       )
    for (days, source) in intervals:
        schedule.every(days).days.do(_crawler(source))

    while(1):
        schedule.run_pending()
        time.sleep(1)
    
