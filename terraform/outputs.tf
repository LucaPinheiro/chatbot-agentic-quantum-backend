output "lambda_arn" {
  value = aws_lambda_function.summarize_lambda.arn
}

output "sqs_url" {
  value = aws_sqs_queue.chatbot_summary_queue.url
}
