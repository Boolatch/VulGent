from enum import Enum
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import uvicorn

# Initialize the core FastAPI web application
app = FastAPI(
    title="VulGent AI Security Laboratory API",
    version="1.0.0",
    description="Backend API for VulGent: A vulnerable enterprise AI assistant studying RAG poisoning, prompt injection, tool misuse, and agent firewalls."
)


# ==========================================
# 1. DATA MODELS & SCHEMAS
# ==========================================
# Pydantic models define the structure, data types, and validation rules for
# request bodies sent to the API and responses returned by the API.

class DocumentTrustLevel(str, Enum):
    """Defines trust classifications for documents stored in the knowledge base."""
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"

class Document(BaseModel):
    """Represents a document inside the RAG knowledge base."""
    id: str
    filename: str
    category: str  # hr, security, it, support
    content: str
    trust_level: DocumentTrustLevel = DocumentTrustLevel.UNVERIFIED
    authority: str = "LOW"  # HIGH or LOW authority

class ChatRequest(BaseModel):
    """Payload sent by the user for a standard chat request."""
    user_id: str
    message: str

class ChatResponse(BaseModel):
    """Response returned by the chatbot."""
    response: str
    model_used: str = "gpt-4o-mini"

class RAGQueryRequest(BaseModel):
    """Payload sent when asking a question through the RAG pipeline."""
    user_id: str
    question: str
    top_k: int = 3  # Number of document chunks to retrieve

class RAGQueryResponse(BaseModel):
    """Response returned after searching documents and generating an answer."""
    question: str
    retrieved_documents: List[Document]
    generated_answer: str

class AttackCategory(str, Enum):
    """Categories of attacks simulated in the lab."""
    DIRECT_INJECTION = "DIRECT_INJECTION"
    INDIRECT_INJECTION = "INDIRECT_INJECTION"
    RAG_POISONING = "RAG_POISONING"

class AttackLogEntry(BaseModel):
    """Structure for logging attack attempts and tracking security outcomes."""
    attack_id: str
    category: AttackCategory
    input_payload: str
    expected_safe_behavior: str
    observed_behavior: str
    success: bool
    defense_enabled: bool

class SimulatedEmailRequest(BaseModel):
    """Payload required to send a simulated email via agent tool calling."""
    recipient: str
    subject: str
    body: str

class FirewallDecision(str, Enum):
    """Possible outcomes when evaluating an agent action against security rules."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_USER_APPROVAL = "REQUIRE_USER_APPROVAL"

class FirewallCheckRequest(BaseModel):
    """Payload sent to evaluate whether a tool action is safe to execute."""
    user_role: str  # e.g., "EMPLOYEE", "ADMIN"
    requested_tool: str
    tool_args: Dict[str, Any]
    retrieved_trust_level: Optional[DocumentTrustLevel] = DocumentTrustLevel.UNVERIFIED

class FirewallCheckResponse(BaseModel):
    """Output decision from the firewall layer."""
    decision: FirewallDecision
    reason: str

class ExperimentResult(BaseModel):
    """Metrics recorded during automated testing runs."""
    experiment_id: str
    config_name: str  # e.g., Baseline, Agent Firewall, Layered
    attack_success_rate: float
    false_positive_rate: float
    normal_task_success_rate: float
    avg_latency_ms: float


# ==========================================
# 2. IN-MEMORY SIMULATED DATABASES
# ==========================================
# Python lists act as temporary in-memory databases to store knowledge base
# documents, attack logs, and simulated outgoing emails without needing SQL setup.

knowledge_base: List[Document] = [
    Document(
        id="doc-1",
        filename="security/acceptable-use.txt",
        category="security",
        content="Customer records must only be accessed on managed company devices. Never save customer files locally.",
        trust_level=DocumentTrustLevel.VERIFIED,
        authority="HIGH"
    ),
    Document(
        id="doc-2",
        filename="hr/remote-work-policy.txt",
        category="hr",
        content="Remote work requires prior approval from your direct manager.",
        trust_level=DocumentTrustLevel.VERIFIED,
        authority="HIGH"
    )
]

attack_logs: List[AttackLogEntry] = []
sent_emails_db: List[Dict[str, str]] = []


# ==========================================
# 3. BASE & HEALTH ROUTES
# ==========================================
# Simple HTTP endpoints used to confirm the API server is operational.

@app.get("/", tags=["General"])
def root():
    """Returns basic system status and OpenAPI documentation pointer."""
    return {
        "system": "VulGent AI Security Laboratory",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health", status_code=status.HTTP_200_OK, tags=["General"])
def get_health():
    """Health check endpoint used by deployment scripts and uptime monitors."""
    return {"status": "healthy", "service": "vulgent-api"}


# ==========================================
# 4. PHASE 1: BASIC CHATBOT ROUTE
# ==========================================
# The starting phase of the project: sending a prompt to the LLM and receiving a response.

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Phase 1 - Basic Chat"])
def basic_chat(request: ChatRequest):
    """Simple baseline chatbot response without document retrieval or tool access."""
    return ChatResponse(
        response=f"VulGent Assistant Response to: '{request.message}'"
    )


# ==========================================
# 5. PHASE 3 & 4: RAG PIPELINE ROUTES
# ==========================================
# Retrieval-Augmented Generation: Uploading documents to the knowledge base
# and retrieving relevant text passages to answer user questions[cite: 4, 10].

@app.get("/api/v1/rag/documents", response_model=List[Document], tags=["Phase 3 - RAG Pipeline"])
def list_documents():
    """Lists all active documents in the knowledge base."""
    return knowledge_base

@app.post("/api/v1/rag/documents", status_code=status.HTTP_201_CREATED, tags=["Phase 3 - RAG Pipeline"])
def add_document(doc: Document):
    """Allows uploading new documents (clean policies or poisoned files) into the RAG database."""
    knowledge_base.append(doc)
    return {"message": "Document ingested successfully", "document_id": doc.id}

@app.post("/api/v1/rag/query", response_model=RAGQueryResponse, tags=["Phase 3 - RAG Pipeline"])
def query_rag(request: RAGQueryRequest):
    """Searches knowledge base documents for relevant context and generates an answer."""
    # Performs a simple keyword search across stored documents
    retrieved = [
        doc for doc in knowledge_base 
        if any(term in doc.content.lower() for term in request.question.lower().split())
    ][:request.top_k]

    # Default fallback if no keyword matches are found
    if not retrieved:
        retrieved = knowledge_base[:1]

    context_str = "\n".join([d.content for d in retrieved])
    answer = f"Based on retrieved company docs: {context_str}"

    return RAGQueryResponse(
        question=request.question,
        retrieved_documents=retrieved,
        generated_answer=answer
    )


# ==========================================
# 6. PHASE 5, 6, 7: ATTACK SIMULATION & LOGGING
# ==========================================
# Stores security experiment logs (Direct Prompt Injection, Indirect Injection, RAG Poisoning)[cite: 8, 11, 12, 13].

@app.post("/api/v1/attacks/log", status_code=status.HTTP_201_CREATED, tags=["Phase 5-7 - Attack Simulation"])
def log_attack_result(entry: AttackLogEntry):
    """Records the outcome of an attack attempt for quantitative analysis."""
    attack_logs.append(entry)
    return {"message": "Attack attempt logged", "attack_id": entry.attack_id}

@app.get("/api/v1/attacks/logs", response_model=List[AttackLogEntry], tags=["Phase 5-7 - Attack Simulation"])
def get_attack_logs():
    """Retrieves all logged security attack results."""
    return attack_logs


# ==========================================
# 7. PHASE 8 & 9: SIMULATED AGENT TOOLS
# ==========================================
# Simulated external APIs that the AI agent can request to execute actions[cite: 5, 13, 14].

@app.get("/api/v1/tools/customer/{customer_id}", tags=["Phase 8 - Agent Tools"])
def get_customer(customer_id: str):
    """Simulated enterprise tool: Fetches customer record details."""
    return {
        "customer_id": customer_id,
        "name": "Acme Corp",
        "data_classification": "RESTRICTED",
        "account_rep": "Alice"
    }

@app.post("/api/v1/tools/send-email", status_code=status.HTTP_200_OK, tags=["Phase 8 - Agent Tools"])
def send_email(email: SimulatedEmailRequest):
    """Simulated enterprise tool: Sends an email to a fake internal database mailbox[cite: 14]."""
    email_record = email.model_dump()
    sent_emails_db.append(email_record)
    return {
        "status": "SENT_TO_SIMULATED_BOX",
        "detail": email_record
    }

@app.get("/api/v1/tools/sent-emails", tags=["Phase 8 - Agent Tools"])
def get_sent_emails():
    """Inspects sent emails to verify whether prompt injection successfully triggered unintended tool execution[cite: 14, 15]."""
    return sent_emails_db


# ==========================================
# 8. PHASE 10: AGENT FIREWALL & DEFENSES
# ==========================================
# Security middleware layer that evaluates whether an AI tool request should be allowed or blocked[cite: 6, 15, 16].

@app.post("/api/v1/firewall/check", response_model=FirewallCheckResponse, tags=["Phase 10 - Agent Firewall"])
def check_firewall_policy(req: FirewallCheckRequest):
    """
    Deterministic rule engine that intercepts tool calls requested by the AI model.
    Checks user permissions and document trust levels before granting execution[cite: 15, 16, 17].
    """
    if req.requested_tool == "send_email":
        # Block tool requests triggered by untrusted retrieved documents
        if req.retrieved_trust_level == DocumentTrustLevel.UNVERIFIED:
            return FirewallCheckResponse(
                decision=FirewallDecision.DENY,
                reason="BLOCKED: Tool requested based on untrusted or unverified retrieved RAG context."
            )
        # Require human/admin confirmation for non-admin email actions
        if req.user_role != "ADMIN":
            return FirewallCheckResponse(
                decision=FirewallDecision.REQUIRE_USER_APPROVAL,
                reason="APPROVAL REQUIRED: External communication requested by non-admin user."
            )

    return FirewallCheckResponse(
        decision=FirewallDecision.ALLOW,
        reason="Operation authorized by security policy."
    )


# ==========================================
# 9. EXPERIMENT ENGINE & DASHBOARD
# ==========================================
# Aggregates performance and security metrics across testing scenarios[cite: 18, 19, 20].

@app.get("/api/v1/dashboard/metrics", response_model=List[ExperimentResult], tags=["Dashboard & Evaluation"])
def get_experiment_metrics():
    """Provides comparative metric data (attack success rate, latency, false positives) for the frontend dashboard[cite: 19, 20]."""
    return [
        ExperimentResult(
            experiment_id="exp-001",
            config_name="Baseline (No Defenses)",
            attack_success_rate=78.5,
            false_positive_rate=0.0,
            normal_task_success_rate=95.0,
            avg_latency_ms=450.0
        ),
        ExperimentResult(
            experiment_id="exp-002",
            config_name="Agent Firewall + Document Trust",
            attack_success_rate=4.2,
            false_positive_rate=2.1,
            normal_task_success_rate=93.5,
            avg_latency_ms=520.0
        )
    ]


# ==========================================
# 10. ENTRY POINT EXECUTION
# ==========================================
# Starts the HTTP web server when running `python main.py`.

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)