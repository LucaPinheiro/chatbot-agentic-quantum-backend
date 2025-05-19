variable "region" {
  default = "us-east-1"
}

variable "openai_api_key" {
  description = "Chave da OpenAI"
}

variable "dynamo_table_name" {
  description = "Nome da tabela DynamoDB"
  default     = "session-chatbot"
}
