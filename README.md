# 🚀 Quantum Tutor Chatbot API

> **An intelligent, multi-agent quantum computing tutoring system powered by RAG (Retrieval Augmented Generation), LLM orchestration, and serverless architecture.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Features](#core-features)
- [System Flow](#system-flow)
- [Technical Deep Dive](#technical-deep-dive)
- [Infrastructure](#infrastructure)
- [API Documentation](#api-documentation)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)

---

## 🎯 Overview

**Quantum Tutor Chatbot API** is a sophisticated educational platform designed to teach quantum computing through an intelligent, context-aware chatbot. The system leverages cutting-edge AI technologies including:

- **RAG (Retrieval Augmented Generation)** for context-aware responses
- **Multi-agent LLM orchestration** with support for multiple models (GPT-4, GPT-3.5, Claude, etc.)
- **Asynchronous message summarization** using AWS SQS and Lambda
- **Hybrid database architecture** (PostgreSQL + DynamoDB)
- **Serverless infrastructure** on AWS

### Key Capabilities

- 🎓 **Personalized Learning**: Each student has sessions tied to classes and groups
- 💬 **Intelligent Conversations**: Context-aware responses using conversation history and summaries
- 📊 **Progress Tracking**: Monitor student progress across topics and classes
- 🔄 **Auto-Summarization**: Automatically condenses long conversations to maintain context
- 🏗️ **Scalable Architecture**: Built for high availability and horizontal scaling

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (Main API)    │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬──────────────┐
    │         │              │              │
┌───▼───┐ ┌──▼───┐    ┌─────▼─────┐  ┌────▼────┐
│PostgreSQL│ │DynamoDB│    │   S3    │  │   SQS   │
│(Relational)│ │(Chat) │    │(Files)  │  │(Queue)  │
└──────────┘ └───────┘    └─────────┘  └────┬────┘
                                            │
                                      ┌─────▼─────┐
                                      │  Lambda   │
                                      │Summarizer │
                                      └───────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115.12 |
| **Language** | Python 3.11+ |
| **LLM** | OpenAI GPT-3.5/GPT-4, LangChain |
| **Relational DB** | PostgreSQL (via SQLAlchemy) |
| **NoSQL DB** | AWS DynamoDB |
| **Object Storage** | AWS S3 |
| **Message Queue** | AWS SQS (FIFO) |
| **Serverless** | AWS Lambda |
| **Authentication** | JWT (PyJWT) |
| **Infrastructure** | Terraform, Docker |

---

## ✨ Core Features

### 1. **Chatbot with RAG & Context Management**

The chatbot maintains conversation context through:
- **Recent Message Window**: Last 8 messages for immediate context
- **Conversation Summaries**: Auto-generated summaries to compress long histories
- **Session-Based Context**: Each conversation is tied to a class/topic for domain-specific responses

### 2. **Multi-Model LLM Router**

Supports multiple LLM providers with intelligent routing:
- GPT-4 (high accuracy, slower)
- GPT-3.5 Turbo (balanced)
- Claude 2 (alternative reasoning)
- Configurable temperature, max tokens, and top-p per model

### 3. **Asynchronous Summarization Pipeline**

When conversations exceed 8 messages:
1. Message is sent to SQS FIFO queue
2. Lambda function processes the queue
3. DynamoDB conversation history is retrieved
4. OpenAI generates a pedagogical summary
5. Summary is stored back in DynamoDB for future context

### 4. **Educational Management System**

- **Users**: Students and administrators
- **Groups**: Class groups for organizing students
- **Classes**: Course instances
- **Topics**: Learning topics within classes
- **Progress Tracking**: Per-topic and per-class progress monitoring

---

## 🔄 System Flow

### Chat Message Flow

```
┌─────────────┐
│   Client    │ POST /api/v1/chat/{session_id}
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  FastAPI Endpoint                   │
│  create_chat_message()              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  1. Save User Message               │
│     → DynamoDB (ChatMessage)       │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  2. Retrieve Context                │
│     - Last 8 messages               │
│     - Previous summary (if exists)  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  3. Generate LLM Response           │
│     → OpenAI API                    │
│     → Context-aware prompt          │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  4. Save System Response            │
│     → DynamoDB                      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  5. Check Summarization Threshold   │
│     If ≥ 8 messages since summary: │
│     → Send to SQS Queue            │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  6. Return Response to Client       │
└─────────────────────────────────────┘
```

### Summarization Flow (Asynchronous)

```
┌─────────────┐
│   SQS Queue │ (FIFO Queue)
│   Message   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda Trigger                     │
│  (Event Source Mapping)              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Lambda Function                    │
│  summarizer.handler()               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  1. Query DynamoDB                  │
│     → Get all messages for session  │
│     → Filter since last summary     │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  2. Retrieve Previous Summary       │
│     (if exists)                      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  3. Generate New Summary            │
│     → OpenAI GPT-3.5                │
│     → Pedagogical prompt            │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  4. Save Summary to DynamoDB        │
│     PK: session#{session_id}        │
│     SK: "summary"                   │
└─────────────────────────────────────┘
```

---

## 🔬 Technical Deep Dive

### 1. **RAG (Retrieval Augmented Generation)**

While the current implementation focuses on conversation context, the architecture supports RAG through:

- **LangChain Integration**: `app/pipelines/chains.py` defines RAG chains
- **Context Injection**: System messages include retrieved information
- **File Storage**: S3 repository for storing educational materials
- **Future Enhancement**: Vector embeddings and semantic search can be integrated

**Current RAG Flow:**
```python
# Context is built from:
1. Conversation summary (if exists)
2. Last 8 messages
3. Class/topic context (from session)
4. Retrieved educational materials (future)
```

### 2. **LLM Service Architecture**

#### OpenAI Service (`app/infra/llm/openai_service.py`)

```python
class OpenAIService:
    - generate_chat_response(): Main chat completion
    - Token tracking: Monitors prompt/completion/total tokens
    - Error handling: Graceful degradation
```

#### LLM Router (`app/infra/llm/llm_router.py`)

```python
class LLMRouter:
    - Multi-model support: GPT-4, GPT-3.5, Claude, Llama
    - Configurable parameters per model
    - Async routing: route_prompt(), route_prompt_to_all()
```

### 3. **Database Architecture**

#### PostgreSQL (Relational Data)

**Tables:**
- `users`: User accounts and authentication
- `groups`: Class groups
- `classes`: Course instances
- `class_topics`: Topics within classes
- `sessions`: Chat sessions
- `topics_progress`: Student progress tracking
- `group_enrollment`: User-group relationships

**Repository Pattern:**
- `app/infra/repositories/*_repository_postgres.py`
- SQLAlchemy ORM with session management
- Transaction support

#### DynamoDB (Chat Messages)

**Table Structure:**
```
PK: session#{session_id}
SK: {timestamp} (for messages) | "summary" (for summaries)

Attributes:
- role: "user" | "system"
- message: string
- tokens: number
- type: "message" | "summary"
- timestamp: ISO8601
```

**Design Patterns:**
- Single-table design
- Partition key: Session ID
- Sort key: Timestamp (enables chronological queries)
- GSI support ready for future queries

### 4. **SQS & Lambda Integration**

#### SQS Queue Configuration

```terraform
resource "aws_sqs_queue" "chatbot_summary_queue" {
  name                         = "chatbot-summarization-queue.fifo"
  fifo_queue                   = true
  content_based_deduplication  = true
}
```

**Why FIFO?**
- Ensures summaries are processed in order
- Prevents duplicate processing
- Maintains message group consistency

#### Lambda Function

**Handler:** `lambda/summarizer.py`

**Responsibilities:**
1. Receive SQS event
2. Query DynamoDB for messages
3. Filter messages since last summary
4. Generate summary via OpenAI
5. Save summary back to DynamoDB

**Environment Variables:**
- `DYNAMO_TABLE`: DynamoDB table name
- `OPENAI_API_KEY`: OpenAI API key

**IAM Permissions:**
- DynamoDB: GetItem, PutItem, Query
- SQS: ReceiveMessage, DeleteMessage
- CloudWatch Logs: Full access

### 5. **Authentication & Authorization**

**JWT-Based Authentication:**
- Token generation: `app/core/jwtoken.py`
- Permission levels: `app/core/permissions.py`
- Roles: Student, Admin

**Security Features:**
- Bearer token authentication
- Permission-based route protection
- Token expiration (configurable)

### 6. **Domain-Driven Design (DDD)**

**Layers:**

1. **Domain Layer** (`app/domain/`)
   - Entities: Business objects (User, Session, ChatMessage, etc.)
   - Interfaces: Repository contracts

2. **Infrastructure Layer** (`app/infra/`)
   - Repository implementations
   - External service integrations (AWS, OpenAI)
   - Database connections

3. **Application Layer** (`app/api/`)
   - Use cases: Business logic
   - Controllers: Request handling
   - Routes: API endpoints

4. **Schemas** (`app/schemas/`)
   - Request/Response models
   - Validation via Pydantic

---

## 🏛️ Infrastructure

### AWS Services Used

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **DynamoDB** | Chat message storage | Single-table design, on-demand billing |
| **S3** | File storage (educational materials) | Bucket per environment |
| **SQS** | Message queue for summarization | FIFO queue |
| **Lambda** | Serverless summarization | Python 3.11 runtime |
| **IAM** | Access control | Least privilege policies |

### Terraform Infrastructure

**Resources:**
- SQS FIFO queue
- Lambda function
- IAM roles and policies
- Event source mapping (SQS → Lambda)

**Environment Management:**
- Multi-stage support: `dev`, `prod`, `test`, `local`
- Environment-specific resource naming
- Variable-based configuration

### Docker & Containerization

**Docker Compose Files:**
- `docker-compose.yml`: Local development
- `docker-compose.dev.yml`: Development environment
- `docker-compose.test.yml`: Testing environment
- `docker-compose.aws.yml`: AWS integration

**Services:**
- PostgreSQL
- Redis (caching, future use)
- FastAPI application

---

## 📚 API Documentation

### Authentication

All protected endpoints require a Bearer token:

```bash
Authorization: Bearer <JWT_TOKEN>
```

### Key Endpoints

#### Chat

```http
POST /api/v1/chat/{session_id}
Content-Type: application/json

{
  "message": "What is quantum superposition?"
}
```

**Response:**
```json
{
  "saved_at": "2024-01-15T10:30:00Z",
  "llm_response": "Quantum superposition is...",
  "llm_tokens": 150,
  "llm_role": "system"
}
```

#### Session Management

```http
GET /api/v1/sessions/{session_id}
```

#### User Management

```http
POST /api/v1/users
GET /api/v1/users/{user_id}
GET /api/v1/users/email/{email}
```

#### Progress Tracking

```http
GET /api/v1/progress/my
GET /api/v1/progress/class/{class_id}
GET /api/v1/progress/group/{group_id}
```

**Full API Documentation:** Available at `/docs` (Swagger UI) when running the application.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose
- AWS Account (for production)
- OpenAI API Key

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd chatbot-agentic-quantum-backend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required Environment Variables:**
```env
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=quantum_chat

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=sa-east-1
AWS_S3_BUCKET=qt-chatbot
DYNAMODB_TABLE_MESSAGES=chat_messages

# OpenAI
OPENAI_API_KEY=your_openai_key

# SQS
SQS_QUEUE_URL=https://sqs.region.amazonaws.com/account/queue

# JWT
JWT_SECRET=your_secret_key
SECRET_KEY=your_secret_key
```

4. **Start with Docker Compose:**
```bash
docker-compose up -d
```

5. **Run database migrations:**
```bash
python app/helpers/functions/create_tables.py
```

6. **Start the application:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Deploying Infrastructure

1. **Initialize Terraform:**
```bash
cd terraform
terraform init
```

2. **Plan changes:**
```bash
terraform plan
```

3. **Apply infrastructure:**
```bash
terraform apply
```

4. **Deploy Lambda:**
```bash
# Package Lambda function
cd lambda
zip -r summarize_lambda.zip .
# Upload via Terraform or AWS CLI
```

---

## 📁 Project Structure

```
chatbot-agentic-quantum-backend/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── endpoints/          # Route handlers
│   │   │   ├── chatbot/        # Chat endpoints
│   │   │   ├── user/           # User management
│   │   │   ├── classes/        # Class management
│   │   │   └── ...
│   │   └── routes.py           # Router aggregation
│   │
│   ├── core/                   # Core functionality
│   │   ├── settings.py         # Configuration
│   │   ├── database_postgres.py
│   │   ├── jwtoken.py          # JWT handling
│   │   └── permissions.py      # Authorization
│   │
│   ├── domain/                 # Domain layer (DDD)
│   │   ├── entities/           # Business entities
│   │   └── interfaces/         # Repository contracts
│   │
│   ├── infra/                  # Infrastructure layer
│   │   ├── repositories/       # Repository implementations
│   │   ├── external/           # External services (AWS)
│   │   └── llm/                # LLM integrations
│   │
│   ├── schemas/                # Pydantic models
│   └── helpers/                # Utilities
│
├── lambda/                     # Lambda function
│   ├── summarizer.py           # Summarization handler
│   └── requirements.txt
│
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── docker/                     # Docker configurations
├── tests/                      # Test suite
├── main.py                     # Application entry point
└── requirements.txt            # Python dependencies
```

---

## 🎓 Educational Context

### Use Case: Quantum Computing Tutoring

The system is designed for teaching quantum computing concepts:

- **Sessions**: Each conversation is tied to a specific class/topic
- **Context Awareness**: Responses consider the current learning topic
- **Progress Tracking**: Monitor student understanding across topics
- **Pedagogical Summaries**: Summaries focus on learning outcomes

### Example Flow

1. Student creates a session for "Quantum Superposition" topic
2. Student asks: "What is quantum superposition?"
3. System retrieves:
   - Previous conversation summary
   - Last 8 messages
   - Topic context
4. LLM generates educational response
5. After 8+ messages, conversation is summarized
6. Summary is used for future context

---

## 🔧 Configuration

### Settings (`app/core/settings.py`)

**Key Configurations:**
- `MESSAGE_SUMMARY_THRESHOLD`: Messages before triggering summary (default: 8)
- `access_token_expire_minutes`: JWT expiration (default: 30)
- `stage`: Environment stage (`dev`, `prod`, `test`, `local`)

### Multi-Environment Support

The system supports multiple environments with:
- Environment-specific database suffixes
- Stage-based S3 bucket naming
- Conditional AWS resource usage

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

---

## 📊 Monitoring & Observability

### Logging

- Structured logging throughout the application
- Token usage tracking for cost monitoring
- Error logging with context

### Metrics (Future)

- Message processing latency
- LLM response times
- SQS queue depth
- Lambda execution metrics

---

## 🔐 Security

- **JWT Authentication**: Secure token-based auth
- **Permission-Based Access**: Role-based authorization
- **AWS IAM**: Least privilege policies
- **Environment Variables**: Sensitive data in env vars
- **Input Validation**: Pydantic schema validation

---



## 📞 Support

For questions or issues, please open an issue in the repository.

---

**Built with ❤️ for quantum computing education**

