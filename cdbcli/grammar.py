from prompt_toolkit.contrib.regular_languages import compiler
from .commands import COMMANDS


def _build_pattern((command, operand_pattern)):
    return "\s*(?P<command>{command})\s+{operand_pattern}".format(command=command,
                                                                  operand_pattern=operand_pattern)


def _create_grammar():
    patterns = map(_build_pattern, [
        (command, operand_pattern)
        for (command, (_, operand_pattern)) in COMMANDS.iteritems()])
    patterns = '|'.join(patterns)
    return compiler.compile(patterns)


grammar = _create_grammar()
