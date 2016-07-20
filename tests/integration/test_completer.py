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


def test_fetch_db_names(environment, couch_server):
    couch_server.create('test1')
    couch_server.create('test2')
    couch_server.create('test3')
    dbnames = completer.fetch_db_names(environment, couch_server)
    assert set(['test1', 'test2', 'test3', '_replicator', '_users']) == set(dbnames)


def test_fetch_doc_ids_no_current_db(environment, couch_server):
    doc_ids = completer.fetch_doc_ids(environment, couch_server)
    assert [] == doc_ids


def test_fetch_doc_ids_with_current_db(environment, couch_server):
    db = couch_server.create('test')
    db.save(get_user_doc('john', 'smith'))
    db.save(get_user_doc('jane', 'doe'))
    environment.current_db = db
    doc_ids = completer.fetch_doc_ids(environment, couch_server)
    assert set(['jane.doe', 'john.smith']) == set(doc_ids)
