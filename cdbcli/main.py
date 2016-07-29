import couchdb
import click

from cdbcli import repl
from cdbcli import __version__ as cdbcli_version

from prompt_toolkit import prompt


class Config():
    def __init__(self, host, port, username, password, tls, database):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__scheme = 'https' if tls else 'http'
        self.database = database

        if not username and password:
            self.__username = 'admin'

    @property
    def username(self):
        return self.__username

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def _cred_string(self):
        if not self.__username or not self.__password:
            return ''

        return '{}:{}@'.format(self.__username, self.__password)

    @property
    def url(self):
        return '{scheme}://{cred}{host}:{port}'.format(
            scheme=self.__scheme, cred=self._cred_string, host=self.__host, port=self.__port)


@click.command()
@click.option('-h', '--host', default='localhost', help='The host of the couchdb instance')
@click.option('--port', default='5984', help='The port of the couchdb instance')
@click.option('-u', '--username', default='admin', help='The username to connect as')
@click.option('-p', '--password', default=None, help='The password')
@click.option('-P', '--askpass/--no-askpass', default=False, help='Ask for password?')
@click.option('--tls/--no-tls', default=False, help='Use TLS to connect to the couchdb instance?')
@click.option('-ver', '--version', is_flag=True)
@click.argument('database', default='', required=False)
def main(host, port, username, password, askpass, tls, version, database):
    if version:
        print_version()

    if askpass:
        password = prompt('Enter password: ', is_password=True)

    config = Config(host, port, username, password, tls, database)
    couch_server = couchdb.Server(config.url)
    r = repl.Repl(couch_server, config)
    r.run()


def print_version():
    import sys
    import os
    print('{} version {}'.format(os.path.basename(sys.argv[0]), cdbcli_version))
    exit()