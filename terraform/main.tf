provider "aws" {
  region = var.region
}

resource "aws_sqs_queue" "chatbot_summary_queue" {
  name                      = "chatbot-summarization-queue.fifo"
  fifo_queue                = true
  content_based_deduplication = true
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-chatbot-summary-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })

  lifecycle {
    prevent_destroy = false
    ignore_changes  = [name]
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-chatbot-policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:Query",
          "dynamodb:PutItem"
        ],
        Resource = "*"
        Effect  = "Allow"
      },
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.chatbot_summary_queue.arn,
        Effect  = "Allow"
      },
      {
        Action = "logs:*",
        Resource = "*",
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_lambda_function" "summarize_lambda" {
  filename         = "lambda/summarize_lambda.zip"
  function_name    = "chatbot_summarize_lambda"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "summarizer.handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("lambda/summarize_lambda.zip")
  timeout          = 15

  environment {
    variables = {
      DYNAMO_TABLE   = var.dynamo_table_name
      OPENAI_API_KEY = var.openai_api_key
    }
  }
}


resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.chatbot_summary_queue.arn
  function_name    = aws_lambda_function.summarize_lambda.arn
  enabled          = true
  batch_size       = 1
}
