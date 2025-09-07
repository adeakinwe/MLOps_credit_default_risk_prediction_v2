#!/usr/bin/env bash

cd "$(dirname "$0")"

LOCAL_TAG=$(date +"%Y-%m-%d-%H-%M")
export LOCAL_IMAGE_NAME="credit_default_predictions:${LOCAL_TAG}"

docker build -t ${LOCAL_IMAGE_NAME} ..

docker-compose up