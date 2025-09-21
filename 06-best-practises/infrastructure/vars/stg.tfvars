source_stream_name = "src-stream-tf"
output_stream_name = "out-stream-tf"
model_bucket = "s3-tf"
ecr_repo_name = "credit-default-prediction-model"
ecr_image_tag = "v1"
/* //////// UNCOMMENT FOR A FRESH DOCKER BUILD AND PUSH TO ECR ////////
lambda_function_local_path = "../lambda_function.py"
docker_image_local_path = "../Dockerfile"
ecr_repo_name = "ecr-tf"
*////////////////////////////////////////////////////////////////////