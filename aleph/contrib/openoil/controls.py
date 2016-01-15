'''
Scripting for openoil tasks

'''

from flask.ext.script import Manager

from aleph.contrib.openoil import scheduled_updates


manager = Manager(usage="openoil admin tasks")

@manager.command
def checkes():
    """
    Check status of ElasticSearch backend
    """
    print('Not implemented')


@manager.command
def schedule():
    """
    Run scrapers by schedule
    """
    scheduled_updates.schedule_updates()
