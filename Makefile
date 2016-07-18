.PHONY: tests

start_couchdb:
	.travis/run-couchdb.sh

stop_couchdb:
	.travis/stop-couchdb.sh

tests:
	py.test --cov=cdbcli --cov=tests --cov-report term-missing tests
