# Make sure to create state bucket beforehand
terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket  = "tf-state-credit-default-risk-prediction"
    key     = "credit-default-risk-prediction-stg.tfstate"
    region  = "eu-west-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

# kinesis source stream #src-stream-tf
module "source_kinesis_stream" {
  source = "./modules/kinesis"
  retention_period = 48
  shard_count = 2
  stream_name = "${var.source_stream_name}-${var.project_id}"
  tags = var.project_id
}

# kinesis output stream # out-stream-tf
module "output_kinesis_stream" {
  source = "./modules/kinesis"
  retention_period = 48
  shard_count = 2
  stream_name = "${var.output_stream_name}-${var.project_id}"
  tags = var.project_id
}

# s3 bucket #s3-tf
module "s3_bucket" {
  source = "./modules/s3"
  bucket_name = "${var.model_bucket}-${var.project_id}"
}

# ecr image registry
module "ecr_image" {
   source = "./modules/ecr"
   ecr_repo_name = "credit-default-prediction-model"
   ecr_image_tag = "v1"
   account_id = local.account_id
}

/*//////// UNCOMMENT FOR A FRESH DOCKER BUILD AND PUSH TO ECR ////////
# ecr image registry #ecr-tf
module "ecr_image" {
   source = "./modules/ecr"
   ecr_repo_name = "${var.ecr_repo_name}-${var.project_id}"
   lambda_function_local_path = var.lambda_function_local_path
   docker_image_local_path = var.docker_image_local_path
   account_id = local.account_id
}
*/////////////////////////////////////////////////////////////////

#lambda function #lambda-tf
module "lambda_function" {
  source = "./modules/lambda"
  image_uri = module.ecr_image.image_uri
  lambda_function_name = "${var.lambda_function_name}-${var.project_id}"
  model_bucket = module.s3_bucket.name
  output_stream_name = "${var.output_stream_name}-${var.project_id}"
  output_stream_arn = module.output_kinesis_stream.stream_arn
  source_stream_name = "${var.source_stream_name}-${var.project_id}"
  source_stream_arn = module.source_kinesis_stream.stream_arn
}

# # For CI/CD
# output "lambda_function" {
#   value     = "${var.lambda_function_name}-${var.project_id}"
# }

# output "model_bucket" {
#   value = module.s3_bucket.name
# }

# output "predictions_stream_name" {
#   value     = "${var.output_stream_name}-${var.project_id}"
# }

# output "ecr_repo" {
#   value = "${var.ecr_repo_name}-${var.project_id}"
# }