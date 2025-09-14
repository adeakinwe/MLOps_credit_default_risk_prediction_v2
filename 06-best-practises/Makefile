LOCAL_TAG := $(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME := credit_default_predictions:${LOCAL_TAG}

test:
	pytest unit_tests/

quality_checks:
	isort .
	black .
	pylint --recursive=y -sn . || true

build: quality_checks test
	docker build -t ${LOCAL_IMAGE_NAME} .

integration_test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} LOCAL_TAG=${LOCAL_TAG} bash integration_test/run-make.sh

publish: build integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} LOCAL_TAG=${LOCAL_TAG} bash scripts/publish.sh

setup:
	pip install pre-commit
	pre-commit install