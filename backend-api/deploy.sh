#!/bin/bash

# Variables
ACR_NAME=plexfloaligndemo
WEBAPP_NAME=alignbackendapi
RESOURCE_GROUP=ALIGNDemo1
IMAGE_NAME=align-fastapi-demo
TAG=latest
IMAGE_URI="$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"

# # Navigate to your project directory (update the path to your project)
# cd /path/to/your/project

# Build the Docker image
docker build --platform linux/amd64 -t $IMAGE_URI .

# Login to Azure Container Registry
az acr login --name $ACR_NAME

# Push the image to Azure Container Registry
docker push $IMAGE_URI

# Update the Web App configuration to use the new image
az webapp config container set \
--name $WEBAPP_NAME \
--resource-group $RESOURCE_GROUP \
--docker-custom-image-name $IMAGE_URI

# Restart the Web App
az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP


# Enable a time to wait 180 seconds before next step
sleep 180

# Echo deployment status
echo "Deployment to $WEBAPP_NAME completed."
