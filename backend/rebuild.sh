#!/bin/bash

echo "Reconstruyendo la imagen del contenedor..."
docker-compose build

echo "Reiniciando los contenedores..."
docker-compose up -d
