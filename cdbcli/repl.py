import couchdb
import prompt_toolkit as pt

from cdbcli import __version__ as cdbcli_version
from prompt_toolkit import history, shortcuts
from .lexer import lexer, split_cli_command_and_shell_commands
from .completer import get_completer
from .style import style
from .grammar import grammar
from .commands import COMMANDS
from .environment import Environment


BANNER = """
      ___  ____  ____   ___  __    ____
     / __)(  _ \(  _ \ / __)(  )  (_  _)
    ( (__  )(_) )) _ <( (__  )(__  _)(_
     \___)(____/(____/ \___)(____)(____)

    Welcome to cdbcli {cdbcli_version}
    CouchDB version: {couchdb_version}

    Type 'help' or 'man' to get a list of all supported commands
    Press <TAB> for command auto-completion
    Press Ctrl+C or Ctrl+D or type 'exit' to exit
"""


def eval_(environment, couch_server, command_text):
    if not command_text:
        return

    cli_command, shell_commands = split_cli_command_and_shell_commands(command_text)

    m = grammar.match_prefix(cli_command)
    if not m:
        raise RuntimeError('Invalid input')

    command = m.variables().get('command')

    if command not in COMMANDS:
        raise RuntimeError('{}: command not found'.format(cli_command))

    handler, _, _ = COMMANDS[command]
    with environment.pipe(shell_commands) as environment:
        handler(environment=environment, couch_server=couch_server, variables=m.variables())


class Repl():
    def __init__(self, couch_server, config, environment=None):
        self._couch_server = couch_server
        self._config = config
        self._environment = environment or Environment()

        try:
            if self._config.database:
                self._environment.current_db = self._couch_server[self._config.database]
        except couchdb.ResourceNotFound:
            self._environment.output("Database '{}' not found".format(self._config.database))

    @property
    def prompt(self):
        if self._environment.current_db:
            database = self._environment.current_db.name
        else:
            database = ''

        privilege_indicator = '#' if self._config.username == 'admin' else '$'
        return '{username}@{host}/{database}{privilege_indicator} '.format(username=self._config.username,
                                                                           host=self._config.host,
                                                                           privilege_indicator=privilege_indicator,
                                                                           database=database)

    def _hello(self):
        message = BANNER.format(cdbcli_version=cdbcli_version,
                                couchdb_version=self._couch_server.version())
        self._environment.output(message)

    def _run(self):
        args = {
            'history': history.InMemoryHistory(),
            'enable_history_search': True,
            'enable_open_in_editor': True,
            'lexer': lexer,
            'completer': get_completer(self._environment, self._couch_server),
            'style': style,
        }
        while True:
            try:
                cli = pt.CommandLineInterface(application=shortcuts.create_prompt_application(self.prompt, **args),
                                              eventloop=shortcuts.create_eventloop())
                self._environment.cli = cli
                cmd_text = cli.run().text.rstrip()
                eval_(self._environment, self._couch_server, cmd_text)
                cli.reset()
            except RuntimeError as e:
                self._environment.output(str(e))
            except (EOFError, KeyboardInterrupt):
                self._environment.output('Exiting...')
                break

    def run(self):
        try:
            self._hello()
        except couchdb.Unauthorized as e:
            self._environment.output('Error connecting to the couchdb instance: {!s}'.format(e))
        else:
            self._run()
