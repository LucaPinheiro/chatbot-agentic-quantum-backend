# output "lambda_arn" {
#   value = aws_lambda_function.summarize_lambda.arn
# }

# output "sqs_url" {
#   value = aws_sqs_queue.chatbot_summary_queue.url
# }

output "app_runner_arn" {
  value       = aws_apprunner_service.fastapi_service.arn
  description = "ARN do serviço App Runner"
}


output "app_runner_url" {
  value       = aws_apprunner_service.fastapi_service.service_url
  description = "URL pública HTTPS do serviço App Runner"
}
