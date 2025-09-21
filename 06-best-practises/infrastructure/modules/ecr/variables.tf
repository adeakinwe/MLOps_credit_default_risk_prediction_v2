variable "ecr_repo_name" {
    type        = string
    description = "ECR repo name"
}

variable "ecr_image_tag" {
    type        = string
    description = "ECR repo name"
    default = "latest"
}

/* //////// UNCOMMENT FOR A FRESH DOCKER BUILD AND PUSH TO ECR ////////
variable "lambda_function_local_path" {
    type        = string
    description = "Local path to lambda function / python file"
}

variable "docker_image_local_path" {
    type        = string
    description = "Local path to Dockerfile"
}
*////////////////////////////////////////////////////////////////////

variable "region" {
    type        = string
    description = "region"
    default = "eu-west-1"
}

variable "account_id" {
}