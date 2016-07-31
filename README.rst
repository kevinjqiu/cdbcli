cdbcli - CouchDB Interactive Shell
==================================

.. image:: https://img.shields.io/pypi/v/cdbcli.svg
   :target: https://pypi.python.org/pypi/cdbcli
   :alt: Latest PyPI version

.. image:: https://travis-ci.org/kevinjqiu/cdbcli.svg?branch=master
   :target: https://travis-ci.org/kevinjqiu/cdbcli
   :alt: Latest Travis CI build status for master

.. image:: https://readthedocs.org/projects/cdbcli/badge/?version=latest
   :target: https://cdbcli.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/kevinjqiu/cdbcli/badge.svg
   :target: https://coveralls.io/github/kevinjqiu/cdbcli
   :alt: Code Coverage

.. image:: https://img.shields.io/badge/license-Apache%202.0-blue.svg
   :target: LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/docker-kevinjqiu%2Fcdbcli-blue.svg
   :target: https://hub.docker.com/r/kevinjqiu/cdbcli/
   :alt: Image on Docker Hub

Features
--------

- auto-completion for database name, document id, view name, command
- syntax highlighting of documents and views
- navigate a couchdb server as if it were a file system
- various commands supported
    * cd - change database
    * ls - list docs under a database
    * cat - show content of a doc
    * exec - execute a view
    * rm - remove a doc
    * man - show help on commands
    * mkdir - create new database
    * du - doc and database size
    * lv - list views inside a view doc
- create/update docs using external ``$EDITOR``
- pipe output to external shell commands, such as ``grep``, ``wc`` and ``jq``

Usage
-----

This tool allows you to traverse a CouchDB database as if it were a file system. Familiar file system commands are supported, such as ``ls``, ``cd``, ``mkdir``, ``rm``, etc, while providing context-rich auto-completion.

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

        Welcome to cdbcli 0.1.1
        CouchDB version: 1.5.0

        Type 'help' or 'man' to get a list of all supported commands
        Press <TAB> for command auto-completion
        Press Ctrl+C or Ctrl+D or type 'exit' to exit

    admin@yourdomain/>

Run with Docker
^^^^^^^^^^^^^^^

``cdbcli`` is also available as a docker image on the `docker hub <https://hub.docker.com/r/kevinjqiu/cdbcli/>`_

To run::

    docker run -it kevinjqiu/cdbcli cdbcli <arguments>

The docker networking restrictions apply, so if you want to connect to a database on localhost, e.g., you will need to let the container use the host's networking::

    docker run -it --net=host kevinjqiu/cdbcli cdbcli <arguments>

Installation
------------

.. code::

    pip install cdbcli


Contributing
------------

* Clone this repository.
* Make a Python virtualenv
* Install requirements: ``pip install -r requirements-test.txt``
* Install `docker <www.docker.com>`_ because the integration tests require it
* Run ``make start_couchdb``. This will start the testing couchdb instance using docker
* Run ``make test``
* Run ``make stop_couchdb`` to clean up

Contributing to Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Clone this repository.
* Make a Python virtualenv
* Install requirements: ``pip install -r requirements-docs.txt``
* Run ``make docs``.  The documentation can be accessed under docs/build/index.html.

Licence
-------

``cdbcli`` is licensed under Apache 2.0


Authors
-------

`cdbcli` was written by `Kevin J. Qiu <kevin@idempotent.ca>`_.

See `all contributors <https://github.com/kevinjqiu/cdbcli/graphs/contributors>`_
