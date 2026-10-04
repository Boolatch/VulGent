# VulGent AI Security Laboratory API

VulGent is a **FastAPI-based AI security laboratory** designed to study how enterprise AI assistants can be attacked and defended.

The project provides a small, self-contained backend for experimenting with:

- Basic AI assistant interactions
- Retrieval-Augmented Generation (RAG)
- RAG document poisoning
- Direct and indirect prompt injection
- AI agent tool misuse
- Document trust levels
- An agent firewall
- Attack logging
- Security experiment metrics

> **Important:** This project is a security research/teaching laboratory. Several components are intentionally simplified or simulated. It is **not a production enterprise AI security system**.

---

## 1. What Does VulGent Do?

The easiest way to think about VulGent is:

```text
User
  |
  v
FastAPI Backend
  |
  +--> Basic Chat
  |
  +--> RAG Knowledge Base
  |      |
  |      +--> Trusted Documents
  |      +--> Untrusted Documents
  |
  +--> Attack Simulation & Logging
  |
  +--> Simulated Agent Tools
  |      |
  |      +--> Customer Data
  |      +--> Send Email
  |
  +--> Agent Firewall
         |
         +--> ALLOW
         +--> DENY
         +--> REQUIRE_USER_APPROVAL
```

The application allows researchers to compare what happens when an AI assistant has **no defenses** versus when security controls such as document trust and an agent firewall are enabled.

---

## 2. Main Security Concepts

### RAG

**Retrieval-Augmented Generation (RAG)** allows an AI system to retrieve information from a knowledge base before generating an answer.

In this project, documents contain:

- An ID
- A filename
- A category
- Content
- A trust level
- An authority level

For example:

```text
ID: doc-1
File: security/acceptable-use.txt
Category: security
Trust: VERIFIED
Authority: HIGH
```

The current implementation uses a simple keyword-based search rather than a real vector database.

### RAG Poisoning

RAG poisoning occurs when an attacker places malicious or misleading information into the documents that an AI system retrieves.

VulGent allows documents to be added through the API so that clean and intentionally poisoned documents can be tested.

### Prompt Injection

Prompt injection attempts to manipulate an AI system into ignoring its intended instructions and performing an unintended action.

The project defines three attack categories:

- `DIRECT_INJECTION`
- `INDIRECT_INJECTION`
- `RAG_POISONING`

### Agent Tool Misuse

An AI agent may have access to tools such as:

- Retrieving customer information
- Sending email

If an attacker can manipulate the model into calling a tool with unsafe arguments, sensitive information could potentially be exposed or an unintended action could occur.

VulGent provides simulated tools so these scenarios can be tested without connecting to real enterprise systems.

### Agent Firewall

The firewall is a deterministic rule engine placed between an AI model and its tools.

It can return:

```text
ALLOW
DENY
REQUIRE_USER_APPROVAL
```

For example, an email action based on an `UNVERIFIED` document is denied.

An email action requested by a non-admin user can require user approval.

---

## 3. Project Structure

The supplied implementation is contained in a Python application, typically named `main.py`.

The main sections are:

```text
main.py
│
├── Data Models & Schemas
│   ├── Document
│   ├── ChatRequest / ChatResponse
│   ├── RAGQueryRequest / RAGQueryResponse
│   ├── AttackLogEntry
│   ├── SimulatedEmailRequest
│   ├── FirewallCheckRequest / FirewallCheckResponse
│   └── ExperimentResult
│
├── In-Memory Databases
│   ├── knowledge_base
│   ├── attack_logs
│   └── sent_emails_db
│
├── General Routes
│   ├── /
│   └── /health
│
├── Basic Chat
│   └── /api/v1/chat
│
├── RAG Pipeline
│   ├── /api/v1/rag/documents
│   └── /api/v1/rag/query
│
├── Attack Simulation
│   ├── /api/v1/attacks/log
│   └── /api/v1/attacks/logs
│
├── Agent Tools
│   ├── /api/v1/tools/customer/{customer_id}
│   ├── /api/v1/tools/send-email
│   └── /api/v1/tools/sent-emails
│
├── Agent Firewall
│   └── /api/v1/firewall/check
│
└── Experiment Dashboard
    └── /api/v1/dashboard/metrics
```

---

# 4. Requirements

You need:

- Python 3.9+ recommended
- FastAPI
- Uvicorn
- Pydantic

Install the dependencies with:

```bash
pip install fastapi uvicorn pydantic
```

If the project includes a `requirements.txt`, you can instead run:

```bash
pip install -r requirements.txt
```

---

# 5. Running the Application

Assuming the Python file is named `main.py`:

```bash
python main.py
```

The application starts on:

```text
http://127.0.0.1:8000
```

The code uses Uvicorn with:

```text
host = 127.0.0.1
port = 8000
reload = True
```

For development, you can also start it with:

```bash
uvicorn main:app --reload
```

---

# 6. API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

This provides an interactive Swagger UI where you can:

1. See all available endpoints
2. Inspect request and response schemas
3. Enter test data
4. Execute API requests
5. Inspect responses

FastAPI also provides an OpenAPI specification through its standard OpenAPI endpoint.

---

# 7. Health Check

## `GET /health`

Checks whether the API is running.

Example:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "vulgent-api"
}
```

This endpoint is intended for deployment scripts and uptime monitoring.

---

# 8. Basic Chat

## `POST /api/v1/chat`

This is the simplest chatbot endpoint.

It accepts:

```json
{
  "user_id": "user-123",
  "message": "What is the security policy?"
}
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "What is the security policy?"
  }'
```

The current implementation returns a simple simulated response.

It does **not** perform RAG retrieval or real model inference.

---

# 9. RAG Knowledge Base

## List Documents

### `GET /api/v1/rag/documents`

Returns all documents currently stored in the in-memory knowledge base.

```bash
curl http://127.0.0.1:8000/api/v1/rag/documents
```

The initial knowledge base contains example company policies.

---

## Add a Document

### `POST /api/v1/rag/documents`

Adds a new document to the knowledge base.

Example:

```json
{
  "id": "doc-3",
  "filename": "security/example.txt",
  "category": "security",
  "content": "This is an example document.",
  "trust_level": "UNVERIFIED",
  "authority": "LOW"
}
```

Example command:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "doc-3",
    "filename": "security/example.txt",
    "category": "security",
    "content": "This is an example document.",
    "trust_level": "UNVERIFIED",
    "authority": "LOW"
  }'
```

The endpoint can be used to simulate both legitimate documents and poisoned documents.

---

# 10. Query the RAG Pipeline

## `POST /api/v1/rag/query`

This endpoint searches the knowledge base and returns documents that match words from the user's question.

Request:

```json
{
  "user_id": "user-123",
  "question": "What are the rules for customer records?",
  "top_k": 3
}
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "question": "What are the rules for customer records?",
    "top_k": 3
  }'
```

The response contains:

- The original question
- Retrieved documents
- A generated answer based on the retrieved document content

### Important implementation detail

The current RAG implementation is intentionally simple.

It does not use:

- Embeddings
- A vector database
- Semantic similarity
- Chunking
- A real LLM

Instead, it checks whether words from the question appear in document content.

This makes the project easy to understand and useful as a starting point for security experiments.

---

# 11. Attack Logging

VulGent can record the result of security experiments.

## Record an Attack

### `POST /api/v1/attacks/log`

Example:

```json
{
  "attack_id": "attack-001",
  "category": "DIRECT_INJECTION",
  "input_payload": "Ignore previous instructions...",
  "expected_safe_behavior": "Refuse the malicious instruction",
  "observed_behavior": "Simulated unsafe response",
  "success": true,
  "defense_enabled": false
}
```

The attack category can be:

```text
DIRECT_INJECTION
INDIRECT_INJECTION
RAG_POISONING
```

---

## View Attack Logs

### `GET /api/v1/attacks/logs`

Returns all attack results recorded during the current application run.

```bash
curl http://127.0.0.1:8000/api/v1/attacks/logs
```

These logs can be used to calculate and compare security metrics.

---

# 12. Simulated Agent Tools

The application provides simulated enterprise tools.

## Get Customer Information

### `GET /api/v1/tools/customer/{customer_id}`

Example:

```bash
curl http://127.0.0.1:8000/api/v1/tools/customer/customer-123
```

The response contains simulated customer information.

The example customer record is marked:

```text
data_classification: RESTRICTED
```

This is a simulated record and does not connect to a real customer database.

---

## Send an Email

### `POST /api/v1/tools/send-email`

Example:

```json
{
  "recipient": "security@example.com",
  "subject": "Security Test",
  "body": "This is a simulated email."
}
```

The endpoint stores the email in an in-memory list rather than sending a real email.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/tools/send-email" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "security@example.com",
    "subject": "Security Test",
    "body": "This is a simulated email."
  }'
```

---

## View Sent Emails

### `GET /api/v1/tools/sent-emails`

Returns the simulated emails that have been created during the current application run.

```bash
curl http://127.0.0.1:8000/api/v1/tools/sent-emails
```

This is useful for checking whether an experiment caused an unintended email action.

---

# 13. Agent Firewall

The firewall is one of the most important security components in the project.

## `POST /api/v1/firewall/check`

The endpoint evaluates whether an AI agent should be allowed to perform a tool action.

Request example:

```json
{
  "user_role": "EMPLOYEE",
  "requested_tool": "send_email",
  "tool_args": {
    "recipient": "security@example.com",
    "subject": "Test",
    "body": "Test message"
  },
  "retrieved_trust_level": "UNVERIFIED"
}
```

The firewall can return one of three decisions:

```text
ALLOW
DENY
REQUIRE_USER_APPROVAL
```

---

## Firewall Rule 1: Unverified RAG Content

If the requested tool is:

```text
send_email
```

and the retrieved document is:

```text
UNVERIFIED
```

the request is denied.

Reason:

```text
Tool requested based on untrusted or unverified retrieved RAG context.
```

This helps prevent an untrusted document from indirectly causing an external action.

---

## Firewall Rule 2: Non-Admin Email Requests

If a user who is not an administrator requests:

```text
send_email
```

and the request passes the trust check, the firewall requires user approval.

The user role must be:

```text
ADMIN
```

to automatically allow the operation.

---

## Firewall Rule 3: Allowed Operations

If none of the blocking conditions apply, the firewall returns:

```text
ALLOW
```

with:

```text
Operation authorized by security policy.
```

---

# 14. Experiment Metrics

## `GET /api/v1/dashboard/metrics`

Returns predefined experiment results for comparing different security configurations.

The current data includes:

### Baseline

```text
Configuration: Baseline (No Defenses)
Attack Success Rate: 78.5
False Positive Rate: 0.0
Normal Task Success Rate: 95.0
Average Latency: 450 ms
```

### Agent Firewall + Document Trust

```text
Configuration: Agent Firewall + Document Trust
Attack Success Rate: 4.2
False Positive Rate: 2.1
Normal Task Success Rate: 93.5
Average Latency: 520 ms
```

These values are currently hard-coded experiment results in the application. They are **not calculated automatically from live attacks**.

---

# 15. Understanding the Security Experiment

A typical experiment can follow this flow:

```text
1. Start with the baseline system
             |
             v
2. Submit an attack
             |
             v
3. Observe the result
             |
             v
4. Record the attack result
             |
             v
5. Enable security controls
             |
             v
6. Run the same attack again
             |
             v
7. Compare the results
```

The main comparison is between:

```text
No Defense
    vs.
Document Trust + Agent Firewall
```

Useful measurements include:

- Attack success rate
- False positive rate
- Normal task success rate
- Average latency

---

# 16. Data Models

The application uses Pydantic models to validate API requests and responses.

## Document

```text
id
filename
category
content
trust_level
authority
```

Trust levels:

```text
VERIFIED
UNVERIFIED
```

---

## ChatRequest

```text
user_id
message
```

---

## RAGQueryRequest

```text
user_id
question
top_k
```

`top_k` controls how many matching documents are returned.

The default is:

```text
3
```

---

## AttackLogEntry

```text
attack_id
category
input_payload
expected_safe_behavior
observed_behavior
success
defense_enabled
```

---

## FirewallCheckRequest

```text
user_role
requested_tool
tool_args
retrieved_trust_level
```

---

## ExperimentResult

```text
experiment_id
config_name
attack_success_rate
false_positive_rate
normal_task_success_rate
avg_latency_ms
```

---

# 17. Current In-Memory Storage

The project currently stores information in Python lists:

```text
knowledge_base
attack_logs
sent_emails_db
```

This means:

- Data exists only while the application is running.
- Restarting the application clears the data.
- There is no persistent database.
- The application is best suited to demonstrations, testing, and research experiments.

For a production system, these would normally be replaced with persistent storage.

---

# 18. Security Architecture

The intended security model can be summarized as:

```text
                 +----------------+
                 |     User       |
                 +-------+--------+
                         |
                         v
                 +----------------+
                 |  AI Assistant  |
                 +-------+--------+
                         |
              +----------+----------+
              |                     |
              v                     v
       +-------------+       +-------------+
       | RAG Search  |       | Agent Tool  |
       +------+------+       +------+------+
              |                     |
              v                     |
       +-------------+              |
       | Document    |              |
       | Trust Check |              |
       +------+------+              |
              |                     |
              +----------+----------+
                         |
                         v
                 +---------------+
                 | Agent Firewall|
                 +-------+-------+
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          ALLOW        DENY     USER APPROVAL
```

The important security idea is that **retrieved information should not automatically be trusted just because it came from the RAG system**.

Similarly, an AI model should not automatically be allowed to execute sensitive tools simply because it requested them.

---

# 19. Example Security Scenario

Imagine a malicious document is added to the RAG knowledge base.

The document is marked:

```text
trust_level = UNVERIFIED
```

An attacker asks the AI assistant a question that causes this document to be retrieved.

The malicious document attempts to influence the assistant to send an email.

Without a security boundary, an agent might attempt:

```text
RAG document
     |
     v
AI model
     |
     v
send_email
```

With the firewall enabled:

```text
RAG document
     |
     v
AI model
     |
     v
Firewall
     |
     v
DENY
```

The firewall blocks the action because the request originated from unverified retrieved context.

This demonstrates the core security principle behind the project:

> **Untrusted information should not automatically become trusted authority for sensitive actions.**

---

# 20. Recommended Development Workflow

When modifying the project, a good workflow is:

### Step 1 — Start the API

```bash
python main.py
```

### Step 2 — Open Swagger UI

```text
http://127.0.0.1:8000/docs
```

### Step 3 — Test the health endpoint

```text
GET /health
```

### Step 4 — Inspect the knowledge base

```text
GET /api/v1/rag/documents
```

### Step 5 — Add a test document

```text
POST /api/v1/rag/documents
```

### Step 6 — Run a RAG query

```text
POST /api/v1/rag/query
```

### Step 7 — Test the simulated tools

Try:

```text
GET /api/v1/tools/customer/{customer_id}
```

and:

```text
POST /api/v1/tools/send-email
```

### Step 8 — Test the firewall

Use:

```text
POST /api/v1/firewall/check
```

with different combinations of:

- User role
- Requested tool
- Document trust level

### Step 9 — Record the experiment

Use:

```text
POST /api/v1/attacks/log
```

### Step 10 — Review metrics

Use:

```text
GET /api/v1/dashboard/metrics
```

---

# 21. Important Limitations

This implementation is intentionally lightweight.

### No real AI model

The basic chat endpoint returns a simulated response. It does not currently call an external LLM.

### No real vector database

RAG retrieval uses simple keyword matching.

### No persistent database

Documents, attack logs, and simulated emails are stored in memory.

### Simulated tools

Customer records and email sending are simulated.

### Hard-coded experiment metrics

Dashboard metrics are predefined values rather than being calculated from a live experiment database.

### Simple firewall

The firewall currently implements a small number of deterministic rules. It is not a complete enterprise policy engine.

### No authentication system

The API accepts `user_id` and `user_role` values as request data. These are not currently backed by a real identity provider or access-control system.

---

# 22. Ideas for Future Improvements

The project can be extended in several directions.

## AI Integration

Connect the application to an actual LLM and implement:

- Model configuration
- Prompt templates
- System instructions
- Tool calling
- Model response evaluation

## Better RAG

Replace keyword matching with:

- Document chunking
- Embeddings
- Vector search
- Metadata filtering
- Citation tracking
- Document provenance

## Persistent Storage

Replace in-memory lists with:

- PostgreSQL
- SQLite for local development
- A document database
- A vector database for RAG

## Stronger Authentication

Add:

- JWT authentication
- OAuth/OIDC
- Role-based access control
- Service identities
- Permission checks

## Better Agent Security

Expand the firewall with:

- Tool allowlists
- Argument validation
- Data classification rules
- User approval workflows
- Rate limits
- Audit trails
- Sensitive-data detection

## Automated Experiments

Build a test runner that automatically:

1. Loads an attack dataset
2. Runs each attack
3. Tests multiple defense configurations
4. Records results
5. Calculates metrics
6. Produces a report

---

# 23. API Endpoint Summary

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Basic system information |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/chat` | Basic chatbot interaction |
| `GET` | `/api/v1/rag/documents` | List RAG documents |
| `POST` | `/api/v1/rag/documents` | Add a RAG document |
| `POST` | `/api/v1/rag/query` | Query the RAG knowledge base |
| `POST` | `/api/v1/attacks/log` | Record an attack result |
| `GET` | `/api/v1/attacks/logs` | Retrieve attack logs |
| `GET` | `/api/v1/tools/customer/{customer_id}` | Retrieve simulated customer data |
| `POST` | `/api/v1/tools/send-email` | Create a simulated email |
| `GET` | `/api/v1/tools/sent-emails` | View simulated emails |
| `POST` | `/api/v1/firewall/check` | Evaluate an agent action |
| `GET` | `/api/v1/dashboard/metrics` | View experiment metrics |

---

# 24. Quick Start

For someone who just wants to run the project:

```bash
# 1. Install dependencies
pip install fastapi uvicorn pydantic

# 2. Start the API
python main.py

# 3. Open the interactive API documentation
# http://127.0.0.1:8000/docs
```

Then start with:

```text
GET /health
```

and explore the endpoints through Swagger UI.

---

# 25. Project Goal

VulGent is intended to make AI security concepts easier to experiment with by providing a controlled environment where developers and researchers can study the relationship between:

```text
AI Models
    +
RAG
    +
Untrusted Data
    +
Agent Tools
    +
Security Policies
```

The central lesson is that **AI output and retrieved information should not automatically be treated as trusted instructions for sensitive actions**.

The project provides a foundation for testing this idea through reproducible attack simulations and defense mechanisms.
