#!/usr/bin/env bash

dropdb doctor_who
dropuser doctor_who
createuser doctor_who --createrole --createdb
createdb doctor_who
# postgres << "CREATE ROLE doctor_who WITH LOGIN PASSWORD 'timemachine'"
# postgres << "GRANT ALL PRIVILEGES ON DATABASE doctor_who TO doctor_who;"
