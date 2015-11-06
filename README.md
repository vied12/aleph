# Aleph

Document-driven investigative tools

This is a collection of tools for ingesting, normalizing, indexing
and tagging documents in the context of a journalistic investigation. 

These tools are intended to be complementary to existing platforms
such as [DocumentCloud](http://documentcloud.org) and [analice.me](http://analice.me).


## Use cases

* As a journalist, I want to store a list of documents that mention
  a person/org/topic so that I can sift through the documents.
* As a journalist, I want to intersect sets of documents that mention
  people/orgs/topics so that I can drill down on the relationships
  between them. 
* As a journalist, I want to combine different types of facets which
  represent document and entity metadata.
* As a data importer, I want to routinely crawl and import documents
  from a data source. 
* As a data importer, I want to associate metadata with documents
  and entities to allow advanced facets. 


## Basic ideas

* An entity (such as a person, organisation, or topic) is always a
  search query; each entity can have multiple actual queries associated
  with it by means of aliases (tags?).
* Documents can be anything, and there is no guarantee that ``dit``
  will be able to display it - just index it. Document display is
  handled by DocumentCloud etc.
* Documents matching an entity after that entity has been created
  yield notifications if a user is subscribed.


## Existing tools

* [DocumentCloud](http://github.com/documentcloud)
* [analice.me](https://github.com/hhba/mapa76)
* [resourcecontracts.org](https://github.com/developmentseed/rw-contracts)
* [mma-dexter](https://github.com/Code4SA/mma-dexter)
* [datawi.re](https://github.com/pudo/datawi.re)
* [nltk](http://www.nltk.org/), [patterns](http://www.clips.ua.ac.be/pattern)
* [OpenCalais](http://www.opencalais.com/), LingPipe, AlchemyAPI


## Installation

### Install Elasticsearch

Either from https://www.elastic.co/downloads/elasticsearch, or using the packages from your distro.

### Install Database

Aleph uses a relational database to keep track of users, crawl state, and other information. 

Postgres is known to work; others supported by sqlalchemy may require some minor code changes. Install postgres, and create a user and blank database for aleph.

### Install node and bower

See https://nodejs.org/en/ and http://bower.io/#install-bower


### Install required packages

On Ubuntu, you can use this command

apt-get install python-dev libxml2-dev libxslt1-dev antiword poppler-utils pstotext tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox virtualenvwrapper default-jre git rabbitmq-server

apt-get build-dep python-psycopg2

and (optional, but useful for deploying):
apt-get install supervisorctl nginx

### Install textract

Textract has external (i.e. non-Python) dependencies. See the [install guide](http://textract.readthedocs.org/en/latest/installation.html).


### Set up aleph

Clone the repository

'''
git clone https://github.com/OpenOil-UG/aleph.git
'''

Install the required python libraries

'''
cd aleph
mkvirtualenv aleph
pip install -r requirements.txt
'''


install and prepare JS and CSS dependencies
'''
make assets
'''

### Configure settings

edit aleph/defaultsettings.py to include correct addresses for your database and your elasticsearch installation, and any other settings you want to tweak

### Start Aleph

First, start the web interface
'''
make web
'''

At this point, you should be able to see a (sparse) web page at http://localhost:5000

To index documents, you will also need to have a worker running in the background. Start it with

'''
make worker
'''


## Index some documents

On the web interface, log in using twitter.
Visit http://localhost:5000/sources/new

This will let you scrape and index some documents using one of the default scrapers.


## License

``aleph`` is licensed under a standard MIT license (included as ``LICENSE``).

