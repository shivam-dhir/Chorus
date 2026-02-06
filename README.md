# Chorus   
**An Event-Driven Workflow Orchestration Platform (Serverless, AWS)**

**Chorus** is a **backend-first, event-driven workflow orchestration platform** built to understand and implement **real-world cloud architecture, distributed systems patterns, and serverless design**.  
The focus of this project is **system design, correctness, observability, and operational boundaries**, not just writing code.

---

## 🧠 Core Idea

**Users define workflows declaratively (JSON)** through an API.  
Chorus stores workflow definitions, manages execution state separately, and lays the foundation for **asynchronous, step-based execution** using cloud primitives.

---

## 🏗️ Current Architecture

**Client (Postman / curl)**  
→ **API Gateway (REST, proxy integration)**  
→ **Workflow API Lambda (Python)**  
→ **DynamoDB (workflows table)**  

Execution workers and async orchestration are implemented incrementally.

---

## ✅ What’s Implemented

### **Workflow Definition API**
- **Public REST endpoint: `POST /workflows`**
- Accepts **declarative workflow definitions (JSON)**
- Persists workflow metadata in DynamoDB
- Fully testable via **Postman**

---

### **Serverless Backend (AWS)**
- **AWS Lambda (Python 3.11)**
  - `chorus-workflow-api` → workflow creation
  - `chorus-worker` → execution groundwork
- **API Gateway (REST API)** for HTTP access
- **DynamoDB** for durable state

---

### **Data Modeling & Separation of Concerns**
- **`workflows` table** → workflow definitions (what should run)
- **`workflow_executions` table** → runtime execution state (what is running)

This separation enables **stateless workers, retries, and scalable orchestration**.

---

### **IAM & Security**
- **Least-privilege IAM roles**
- Explicit access only to required DynamoDB tables
- **No hardcoded credentials**
- Lambdas rely on **assumed roles at runtime**

---

### **Observability & Debugging**
- **Structured logging with CloudWatch**
- Debugged **real API Gateway → Lambda payload shape differences**
- Defensive request parsing for **proxy and non-proxy events**

---

### **Local-First Development**
- Single project-scoped Python virtual environment (`.venv`)
- Local Lambda testing before deployment
- Clear boundary between **local runtime vs AWS runtime**
- No console-only shortcuts

---

## 🧪 Testing the API

**Endpoint**
- POST https://kjaibtnwnc.execute-api.us-east-2.amazonaws.com/dev/workflows

**Headers**
- Content-Type: application/json

**Sample Request**
```json
{
  "workflow_id": "example_workflow",
  "definition": {
    "steps": [
      {
        "type": "log",
        "message": "hello chorus"
      }
    ]
  }
}
```

**Successful Response**
```json
{
  "message": "Workflow created",
  "workflow_id": "example_workflow"
}
```

 ## Tech Stack

- Language: Python 3.11
- Cloud: AWS
- Compute: AWS Lambda
- API: API Gateway (REST)
- Storage: DynamoDB
- Security: IAM
- Observability: CloudWatch Logs
- Tooling: Postman, AWS CLI

## Roadmap

**Planned next steps**:

- Workflow execution endpoint (POST /workflows/{id}/execute)

- Asynchronous execution with SQS

- Retries, idempotency, and failure handling

- Rate limiting and API throttling

- Metrics and dashboards (CloudWatch → Prometheus/Grafana)

- CI/CD pipelines for Lambda deployments

- Containerized workers and Kubernetes (future phase)

## Project Philosophy
**Chorus is intentionally built to**:

- Model production-style backend systems

- Emphasize architecture and failure modes

- Expose real cloud integration issues

- Prioritize clarity, correctness, and observability

## Status

Actively under development, features are added incrementally with a focus on system design and real-world behavior.
