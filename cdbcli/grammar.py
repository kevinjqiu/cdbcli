from prompt_toolkit.contrib.regular_languages import compiler
from .commands import COMMANDS


def _create_grammar():
    command_pattern = '|'.join(COMMANDS.keys())
    return compiler.compile("""\
(\s*(?P<command>{})\s+(?P<operand>.*))
                            """.format(command_pattern))

grammar = _create_grammar()
