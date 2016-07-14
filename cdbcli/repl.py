from __future__ import print_function

import couchdb

import prompt_toolkit as pt
from prompt_toolkit import history
from .lexer import lexer
from .completer import get_completer
from .style import style
from .grammar import grammar
from .commands import COMMANDS
from .context import Context


BANNER = """
      ___  ____  ____   ___  __    ____
     / __)(  _ \(  _ \ / __)(  )  (_  _)
    ( (__  )(_) )) _ <( (__  )(__  _)(_
     \___)(____/(____/ \___)(____)(____)

    Welcome to cdbcli
    CouchDB version: {couchdb_version}

    Press <TAB> for command auto-completion
    Press Ctrl+C or Ctrl+D or type 'exit' to exit
"""


class Repl(object):
    def __init__(self, couch_server, config):
        self._couch_server = couch_server
        self._config = config
        self._context = Context()

        try:
            if self._config.database:
                self._context.current_db = self._couch_server[self._config.database]
        except couchdb.ResourceNotFound:
            print("Database '{}' not found".format(self._config.database))

    @property
    def prompt(self):
        if self._context.current_db:
            database = self._context.current_db.name
        else:
            database = ''

        return u'{username}@{host}/{database}> '.format(username=self._config.username,
                                                        host=self._config.host,
                                                        database=database)

    def _hello(self):
        message = BANNER.format(couchdb_version=self._couch_server.version())
        print(message)

    def _run(self):
        while True:
            try:
                args = {
                    'history': history.InMemoryHistory(),
                    'enable_history_search': True,
                    'lexer': lexer,
                    'completer': get_completer(self._couch_server, self._context),
                    'style': style,
                }
                cmd_text = pt.prompt(self.prompt, **args).rstrip()

                if not cmd_text:
                    continue

                m = grammar.match_prefix(cmd_text)
                if not m:
                    raise RuntimeError('Invalid input')

                command = m.variables().get('command')

                if command not in COMMANDS:
                    raise RuntimeError('{} is not a recognized command'.format(command))

                handler, _ = COMMANDS[command]
                handler(context=self._context, couch_server=self._couch_server, variables=m.variables())
            except RuntimeError as e:
                print(str(e))
            except (EOFError, KeyboardInterrupt):
                print('Exiting...')
                break

    def run(self):
        try:
            self._hello()
        except couchdb.Unauthorized as e:
            print('Error connecting to the couchdb instance: {!s}'.format(e))
        else:
            self._run()
