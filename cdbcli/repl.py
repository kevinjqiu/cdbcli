from __future__ import print_function
import couchdb

import prompt_toolkit as pt
from prompt_toolkit import history


BANNER = """
      ___  ____  ____   ___  __    ____
     / __)(  _ \(  _ \ / __)(  )  (_  _)
    ( (__  )(_) )) _ <( (__  )(__  _)(_
     \___)(____/(____/ \___)(____)(____)

    Welcome to cdbcli
    CouchDB version: {couchdb_version}

    Enter \h for help
"""

class Repl(object):
    def __init__(self, couch_server, config):
        self._couch_server = couch_server
        self._config = config

    @property
    def prompt(self):
        return '{username}@{host}{database}'.format(username=self._config.username,
                                                    host=self._config.host, database=self._config.database)

    def _hello(self):
        message = BANNER.format(couchdb_version=self._couch_server.version())
        print(message)

    def _run(self):
        while True:
            try:
                args = {
                    'history': history.InMemoryHistory(),
                    'enable_history_search': True,
                }
                cmd = pt.prompt(u"{}> ".format(self.prompt), **args)
                print('You entered: ', cmd)
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
