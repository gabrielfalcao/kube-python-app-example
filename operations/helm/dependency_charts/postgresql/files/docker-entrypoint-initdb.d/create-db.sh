#!/bin/bash

set -x;


cat <<EOF | psql -U postgres
drop database $POSTGRES_DB;
create database $POSTGRES_DB;
create user $POSTGRES_USER;
alter role $POSTGRES_USER with password '$POSTGRES_PASSWORD';
grant all privileges on database $POSTGRES_DB to $POSTGRES_USER;
alter database $POSTGRES_DB owner to $POSTGRES_USER;
EOF
