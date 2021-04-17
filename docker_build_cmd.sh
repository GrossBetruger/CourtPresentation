docker stop local_servile
docker rm local_servile
docker build -t local_servile_image . --network host
docker run --name local_servile -e POSTGRES_PASSWORD=password local_servile_image  

