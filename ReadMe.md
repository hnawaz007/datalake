# Trino with Iceberg, Postgres, and MinIO

This is the datalake setup using Trino with an Iceberg connector, Postgres as metastore, and MinIO for object storage.

Start everything up:
```shell
docker-compose up
```

Connect to the Trino controller to execute some SQL:
```shell
docker-compose exec controller trino
```

Stop and remove the containers and network:
```shell
docker-compose down
```

