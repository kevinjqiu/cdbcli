from cdbcli.main import Config


def test_no_cred_str_if_neither_username_password_given():
    cfg = Config('localhost', 5984, None, None, False, '')
    assert cfg.url == 'http://localhost:5984/'


def test_cred_str_when_only_username_is_given():
    cfg = Config('localhost', 5984, 'user', None, False, '')
    assert cfg.url == 'http://user@localhost:5984/'


def test_cred_str_when_username_and_password_given():
    cfg = Config('localhost', 5984, 'user', 'pwd', False, '')
    assert cfg.url == 'http://user:pwd@localhost:5984/'


def test_cred_str_default_username_to_admin_when_only_pwd_given():
    cfg = Config('localhost', 5984, None, 'pwd', False, '')
    assert cfg.url == 'http://admin:pwd@localhost:5984/'
