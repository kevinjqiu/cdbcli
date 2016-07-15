from cdbcli.grammar import grammar


def _assert_grammar_match(cmd_text, **expected):
    m = grammar.match(cmd_text)
    assert m is not None
    for key, value in expected.iteritems():
        assert m.variables().get(key) == value


def test_cd():
    cmd_text = 'cd blah'
    _assert_grammar_match(cmd_text, command='cd', database_name='blah')


def test_cat():
    cmd_text = 'cat xyz'
    _assert_grammar_match(cmd_text, command='cat', doc_id='xyz')
