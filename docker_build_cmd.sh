docker stop local_servile
docker rm local_servile
docker build -t local_servile_image . --network host
docker volume create servile_db 
docker run --name local_servile -v servile_db:/var/lib/postgresql/data -e POSTGRES_PASSWORD=password local_servile_image  

