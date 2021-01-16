#/bin/bash

set -e

pg_dump --table testers --data-only --user postgres --column-inserts 
