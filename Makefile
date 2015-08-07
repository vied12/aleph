
web:
	python aleph/manage.py runserver

worker:
	celery -A aleph.queue -c 15 -l INFO worker -n `cat /proc/sys/kernel/random/uuid`


# single-threded worker with lots of debug logging, on a separate queue
debugworker:
	celery -A aleph.queue -c 1 -l DEBUG worker -n `cat /proc/sys/kernel/random/uuid`

clear:
	celery purge -f -A aleph.queue

assets:
	bower install
	python aleph/manage.py assets --parse-templates build
