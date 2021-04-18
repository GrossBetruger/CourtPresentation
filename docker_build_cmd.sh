docker stop local_servile
docker rm local_servile
docker build -t local_servile_image . --network host
docker volume create servile_db 
docker run --name local_servile -p 5432:5432 -v servile_db:/var/lib/postgresql/data -e POSTGRES_PASSWORD=password local_servile_image  

