cdbcli
======

.. image:: https://img.shields.io/pypi/v/cdbcli.svg
    :target: https://pypi.python.org/pypi/cdbcli
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/kevinjqiu/cdbcli.png
   :target: https://travis-ci.org/kevinjqiu/cdbcli
   :alt: Latest Travis CI build status

The interactive CLI for CouchDB

Usage
-----

This tool allows you to traverse a CouchDB database as if it were a file system. Familiar file system commands are supported, such as ``ls``, ``cd``, ``mkdir``, ``rm``, etc.

Starting cdbcli
^^^^^^^^^^^^^^^

Refer to the Installation_ section for guide on how to install cdbcli.

Running cdbcli requires connection parameters to the underlying couchdb instance you want to connnect to.

.. code::

	cdbcli --help

	Usage: cdbcli [OPTIONS] [DATABASE]

	Options:
	  -h, --host TEXT               The host of the couchdb instance
	  --port TEXT                   The port of the coouchdb instance
	  -u, --username TEXT           The username to connect as
	  -p, --password TEXT           The password
	  -P, --askpass / --no-askpass  Ask for password?
	  --tls / --no-tls              Use TLS to connect to the couchdb instance?
	  --help                        Show this message and exit.

e.g., if you want to connect your couchdb instance at http://yourdomain:9999, you can issue the command::

    cdbcli -h yourdomain --port 9999 -u admin -P

Specifying ``-P`` will prompt you for password. You can also use ``-p`` to specify password at the command line, but this is not recommended for sensitive passwords.

By default, ``cdbcli`` connects to the couchdb instance at http://localhost:5984.


You will be greeted by the cdbcli's splash screen::

          ___  ____  ____   ___  __    ____
         / __)(  _ \(  _ \ / __)(  )  (_  _)
        ( (__  )(_) )) _ <( (__  )(__  _)(_
         \___)(____/(____/ \___)(____)(____)

        Welcome to cdbcli
        CouchDB version: 1.5.0

        Press <TAB> for command auto-completion
        Press Ctrl+C or Ctrl+D or type 'exit' to exit

    admin@www.idempotent.ca/>

Installation
------------

.. code::

    pip install cdbcli

Requirements
^^^^^^^^^^^^

Licence
-------

Authors
-------

`cdbcli` was written by `Kevin J. Qiu <kevin@idempotent.ca>`_.
