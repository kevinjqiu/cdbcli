from prompt_toolkit.contrib.regular_languages import compiler
from .commands import COMMANDS


def _build_pattern((command, operand_pattern)):
    # compiler tokenizes the pattern, as a result, the space in the pattern
    # string are stripped out
    command_pattern = command.replace(' ', '\s')
    if operand_pattern:
        return "(\s*(?P<command>{command_pattern})\s+{operand_pattern})".format(command_pattern=command_pattern,
                                                                                operand_pattern=operand_pattern)
    else:
        return "(\s*(?P<command>{command_pattern}))".format(command_pattern=command_pattern)


def _create_grammar():
    patterns = map(_build_pattern, [
        (command, operand_pattern)
        for (command, (_, operand_pattern)) in COMMANDS.iteritems()])
    patterns = '|'.join(patterns)
    return compiler.compile(patterns)


grammar = _create_grammar()
