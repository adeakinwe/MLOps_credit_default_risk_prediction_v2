#!/usr/bin/env bash

echo "publishing image ${LOCAL_IMAGE_NAME} to ECR..."
# set -euo pipefail

# # Ensure variables are passed from Makefile
# : "${LOCAL_IMAGE_NAME:?LOCAL_IMAGE_NAME is required}"
# : "${LOCAL_TAG:?LOCAL_TAG is required}"

# # Your remote ECR URI
# REMOTE_URI="928475935048.dkr.ecr.eu-west-1.amazonaws.com/credit-default-prediction-model"

# echo "📦 Publishing image ${LOCAL_IMAGE_NAME} to ${REMOTE_URI}:${LOCAL_TAG}..."

# # Authenticate Docker to ECR
# aws ecr get-login-password --region eu-west-1 \
#   | docker login --username AWS --password-stdin 928475935048.dkr.ecr.eu-west-1.amazonaws.com

# # Tag the local image with the remote URI
# docker tag "${LOCAL_IMAGE_NAME}" "${REMOTE_URI}:${LOCAL_TAG}"

# # Push to ECR
# docker push "${REMOTE_URI}:${LOCAL_TAG}"

# echo "✅ Successfully published ${REMOTE_URI}:${LOCAL_TAG}"