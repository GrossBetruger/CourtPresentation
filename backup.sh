#!/bin/bash

set -e 

docker exec -it local_servile bash -c 'mkdir -p /home/servile_backup; pg_dump --host localhost -U postgres > /home/servile_backup/servile_backup.sql'

mkdir -p Backup

filename="servile_backup_$(date | awk '{print $2$3$4}').sql"

docker cp local_servile:/home/servile_backup/servile_backup.sql Backup/$filename

zip Backup/"$filename".zip Backup/$filename
rm Backup/$filename
