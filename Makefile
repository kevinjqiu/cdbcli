.PHONY: tests

start_couchdb:
	.travis/start-couchdb.sh

stop_couchdb:
	.travis/stop-couchdb.sh

test:
	py.test --cov=cdbcli --cov=tests --cov-report term-missing tests
