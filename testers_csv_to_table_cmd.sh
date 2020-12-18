#/bin/bash

set -e 

pgcsv --db 'postgresql://localhost/postgres?user=postgres&password=...' testers testers.csv

