import uuid
import couchdb
import pytest

from cStringIO import StringIO
from cdbcli.environment import Environment


INTEGRATION_TEST_COUCHDB_URL = 'http://admin:password@localhost:5984/'


@pytest.fixture
def environment():
    output_stream = StringIO()
    return Environment(None, output_stream)


@pytest.fixture
def couch_server():
    couch_server = couchdb.Server(INTEGRATION_TEST_COUCHDB_URL)
    for db in couch_server:
        if db not in ['_replicator', '_users']:
            del couch_server[db]

    return couch_server


def get_user_doc(first_name=None, last_name=None):
    first_name = first_name or uuid.uuid4().hex
    last_name = last_name or uuid.uuid4().hex

    return dict(
        _id='{}.{}'.format(first_name, last_name),
        first_name=first_name,
        last_name=last_name,
    )


def get_user_design_doc():
    return {
        '_id': '_design/users',
        'language': 'python',
        'views': {
            'by_lastname': {
                'map': 'def map(doc): yield doc.get("last_name"), doc'
            },
            'by_firstname': {
                'map': 'def map(doc): yield doc.get("first_name"), doc'
            }
        }
    }
