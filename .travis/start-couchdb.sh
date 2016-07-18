#! /bin/bash
docker run -d --name couchdb -p 5984:5984 -e COUCHDB_PASS="password" kevinjqiu/couchdb
