#!/bin/bash

docker ps -aq | xargs docker stop | xargs docker rm
echo "[1] Docker containers stopped and removed."
docker build --tag align-fastapi-demo .
echo "[2] Docker build completed."
docker run -d -p 3100:3100 --name alignbackendapi align-fastapi-demo
echo "[3] Docker container started."
echo "Go to http://localhost:3100/docs to see the API documentation."