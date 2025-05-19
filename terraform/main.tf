provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

# resource "aws_sqs_queue" "chatbot_summary_queue" {
#   name                        = "chatbot-summarization-queue.fifo"
#   fifo_queue                  = true
#   content_based_deduplication = true
# }

# # ------------------------------
# # lambda function
# # ------------------------------

# resource "aws_iam_role" "lambda_exec_role" {
#   name = "lambda-chatbot-summary-role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [{
#       Effect = "Allow",
#       Principal = {
#         Service = "lambda.amazonaws.com"
#       },
#       Action = "sts:AssumeRole"
#     }]
#   })

#   lifecycle {
#     prevent_destroy = false
#     ignore_changes  = [name]
#   }
# }

# resource "aws_iam_role_policy" "lambda_policy" {
#   name = "lambda-chatbot-policy"
#   role = aws_iam_role.lambda_exec_role.id

#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Effect = "Allow",
#         Action = [
#           "dynamodb:GetItem",
#           "dynamodb:PutItem",
#           "dynamodb:UpdateItem",
#           "dynamodb:Query"
#         ],
#         Resource = "arn:aws:dynamodb:${var.region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamo_table_name}"
#       },
#       {
#         Effect = "Allow",
#         Action = [
#           "sqs:ReceiveMessage",
#           "sqs:DeleteMessage",
#           "sqs:GetQueueAttributes"
#         ],
#         Resource = aws_sqs_queue.chatbot_summary_queue.arn
#       },
#       {
#         Effect   = "Allow",
#         Action   = "logs:*",
#         Resource = "*"
#       }
#     ]
#   })
# }

# resource "aws_lambda_function" "summarize_lambda" {
#   depends_on       = [aws_iam_role_policy.lambda_policy]
#   filename         = "lambda/summarize_lambda.zip"
#   function_name    = "chatbot_summarize_lambda"
#   role             = aws_iam_role.lambda_exec_role.arn
#   handler          = "summarizer.handler"
#   runtime          = "python3.11"
#   publish          = true
#   source_code_hash = filebase64sha256("lambda/summarize_lambda.zip")
#   timeout          = 15

#   environment {
#     variables = {
#       DYNAMO_TABLE   = var.dynamo_table_name
#       OPENAI_API_KEY = var.openai_api_key
#     }
#   }

#   lifecycle {
#     prevent_destroy       = false
#     create_before_destroy = true
#   }
# }

# resource "aws_lambda_event_source_mapping" "sqs_trigger" {
#   event_source_arn = aws_sqs_queue.chatbot_summary_queue.arn
#   function_name    = aws_lambda_function.summarize_lambda.arn
#   enabled          = true
#   batch_size       = 1

#   depends_on = [aws_lambda_function.summarize_lambda]

#   lifecycle {
#     create_before_destroy = true
#     prevent_destroy       = false
#   }
# }

# ------------------------------
# App Runner Service
# ------------------------------

resource "aws_ecr_repository" "fastapi_app" {
  name = "fastapi-app"
}

resource "aws_iam_role" "apprunner_ecr_access" {
  name = "AppRunnerECRAccessRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_read_policy" {
  role       = aws_iam_role.apprunner_ecr_access.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}


resource "aws_apprunner_service" "fastapi_service" {
  service_name = "fastapi-app-service"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.fastapi_app.repository_url}:latest"
      image_repository_type = "ECR"
      image_configuration {
        port = "8000"
      }
    }

    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu    = "512"
    memory = "1024"
  }

  depends_on = [aws_iam_role_policy_attachment.ecr_read_policy]
}
