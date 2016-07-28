.PHONY: tests

start_couchdb:
	.travis/start-couchdb.sh

stop_couchdb:
	.travis/stop-couchdb.sh

flake8:
	flake8 --max-line-length=120 --ignore=F405 cdbcli tests

test: flake8
	py.test --cov=cdbcli --cov=tests --cov-report term-missing tests
