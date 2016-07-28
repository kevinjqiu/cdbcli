from cdbcli.lexer import split_cli_command_and_shell_commands


def test_split_cli_command_no_shell_commands():
    cli_command, shell_commands = split_cli_command_and_shell_commands('cat foobar')
    assert cli_command == 'cat foobar'
    assert shell_commands == []


def test_split_cli_command_and_one_shell_command():
    cli_command, shell_commands = split_cli_command_and_shell_commands('cat foobar | grep ID')
    assert cli_command == 'cat foobar'
    assert shell_commands == ['grep ID']


def test_split_cli_command_and_multiple_shell_commands():
    cli_command, shell_commands = split_cli_command_and_shell_commands('cat foobar | grep ID | uniq | sort')
    assert cli_command == 'cat foobar'
    assert shell_commands == ['grep ID', 'uniq', 'sort']


def test_split_cli_command_and_multiple_shell_commands_with_space_in_quotes():
    cli_command, shell_commands = split_cli_command_and_shell_commands('cat foobar | grep ID | cut -d " " -f 2')
    assert cli_command == 'cat foobar'
    assert shell_commands == ['grep ID', "cut -d ' ' -f 2"]
