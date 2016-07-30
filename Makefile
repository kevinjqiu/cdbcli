.PHONY: tests docs

REPO=kevinjqiu/cdbcli

start_couchdb:
	.travis/start-couchdb.sh

stop_couchdb:
	.travis/stop-couchdb.sh

flake8:
	flake8 --max-line-length=120 --ignore=F405 cdbcli tests

test: flake8
	py.test --cov=cdbcli --cov=tests --cov-report term-missing tests

docs: clean_docs
	sphinx-build -b html docs docs/build

clean_docs:
	rm docs/build -rvf

build_docker:
	docker build -t $(REPO) .
