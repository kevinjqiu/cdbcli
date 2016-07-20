from tests.integration.fixtures import *  # noqa
from cdbcli import completer


def test_fetch_view_path_no_current_db(environment, couch_server):
    view_paths = completer.fetch_view_paths(environment, couch_server)
    assert [] == view_paths


def test_fetch_view_path_with_current_db(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_user_design_doc())
    environment.current_db = db
    view_paths = completer.fetch_view_paths(environment, couch_server)
    assert set(['_design/users:by_lastname', '_design/users:by_firstname']) == set(view_paths)


def test_fetch_view_ids_no_current_db(environment, couch_server):
    view_paths = completer.fetch_view_ids(environment, couch_server)
    assert [] == view_paths


def test_fetch_view_ids_with_current_db(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_user_design_doc())
    environment.current_db = db
    view_paths = completer.fetch_view_ids(environment, couch_server)
    assert set(['_design/users']) == set(view_paths)
