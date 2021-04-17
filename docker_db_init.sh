
docker exec -it local_servile psql -U postgres -c "\copy testers from '/var/lib/postgresql/data/testers.csv'" 
