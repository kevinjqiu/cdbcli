from cdbcli.grammar import grammar


def _assert_grammar_match(cmd_text, **expected):
    m = grammar.match(cmd_text)
    assert m is not None
    for key, value in expected.iteritems():
        assert m.variables().get(key) == value


def test_leading_spaces_are_ignored():
    cmd_text = '   USE blah'
    _assert_grammar_match(cmd_text, command='USE', operand='blah')


def test_trailing_spaces_are_not_ignored():
    cmd_text = 'USE blah    '
    _assert_grammar_match(cmd_text, command='USE', operand='blah    ')
