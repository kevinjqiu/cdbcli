import couchdb
import pytest

from cStringIO import StringIO
from cdbcli.environment import Environment


@pytest.fixture
def environment():
    output_stream = StringIO()
    return Environment(None, output_stream)


@pytest.fixture
def couch_server():
    couch_server = couchdb.Server('http://admin:password@localhost:5984/')
    for db in couch_server:
        if db not in ['_replicator', '_users']:
            del couch_server[db]

    return couch_server
