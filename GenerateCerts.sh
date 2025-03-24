#!/bin/bash

set -e

echo "Generating SSL/TLS certificates..."

openssl genrsa -out server/server.key 2048
openssl req -new -key server/server.key -out server/server.csr -config server/server.cnf
openssl x509 -req -days 365 -in server/server.csr -signkey server/server.key -out server/server.crt
cp server/server.crt client/server.crt

echo "Certificates successfully generated"