variable "region" {
  default = "us-east-1"
}

variable "dynamo_table_name" {
  description = "Nome da tabela DynamoDB"
}

variable "openai_api_key" {
  description = "Chave da OpenAI"
}

variable "dynamo_table_name" {
  description = "Nome da tabela DynamoDB"
  default     = "session-chatbot"
}