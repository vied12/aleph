import logging
from hashlib import sha1
from pkg_resources import iter_entry_points

from aleph.core import db
from aleph.model import CrawlState
from aleph.processing import ingest_url, ingest

from aleph.contrib.openoil.metadata import guess_filing_date_from_meta

log = logging.getLogger(__name__)
CRAWLERS = {}


def get_crawlers():
    if not CRAWLERS:
        for ep in iter_entry_points('aleph.crawlers'):
            CRAWLERS[ep.name] = ep.load()
    return CRAWLERS


class TagExists(Exception):
    pass


class Crawler(object):

    def __init__(self, source, ignore_tags=False):
        self.source = source
        self.ignore_tags = ignore_tags

    def crawl(self):
        raise NotImplemented()

    def meta_data(self, title=None, mime_type=None, extension=None,
                  source_url=None, source_file=None, article=False,
                  summary=None, meta=None):
        if meta is None:
            meta = {}
        meta.update({
            'title': title,
            'summary': summary,
            'mime_type': mime_type,
            'extension': extension,
            'source_url': source_url,
            'source_file': source_file,
            'extract_article': article,
        })
        filed_at = guess_filing_date_from_meta(meta)
        meta['filed_at'] = filed_at.strftime('%Y%m%d') if filed_at else None
        return dict([(k, v) for k, v in meta.items() if v is not None])

    def emit_url(self, url, package_id=None, **kwargs):
        meta = self.meta_data(**kwargs)
        meta['source_url'] = url
        ingest_url.delay(self.source.slug, url,
                         package_id=package_id, meta=meta)

    def emit_ingest(self, something, package_id=None, **kwargs):
        meta = self.meta_data(**kwargs)
        ingest(self.source.store, something,
               package_id=package_id, meta=meta)

    def make_tag(self, title=None, url=None, **kwargs):
        kwargs['title'] = title
        kwargs['url'] = url

        kwjoin = []
        for k,v in kwargs.items():
            if isinstance(v, unicode):
                kwjoin.append(repr((k,v)))
            else:
                kwjoin.append(repr((k,unicode(v or '', errors='replace'))))
        #kwargs = [repr((k, unicode(v or '', errors='replace'))) for k, v in kwargs.items()]
        return sha1('$'.join(kwjoin)).hexdigest()

    def check_tag(self, tag=None, title=None, url=None, **kwargs):
        if tag is None:
            tag = self.make_tag(title=title, url=url, **kwargs)
        if not self.ignore_tags:
            if CrawlState.check(tag):
                log.debug("Skipping %r in %r, tagged as done.", tag, self.source)
                raise TagExists()
            CrawlState.create(self.source, tag)
            db.session.commit()
        return tag

    def __repr__(self):
        return '<%s(%r)>' % (self.__class__.__name__, self.source)
