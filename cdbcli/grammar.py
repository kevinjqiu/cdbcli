from prompt_toolkit.contrib.regular_languages import compiler


def _create_grammar():
    return compiler.compile("""\
(\s*(?P<command>[a-zA-Z]+)\s+(?P<operand>)\s*)
                            """)

grammar = _create_grammar()
