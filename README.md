VulGent
VulGent is an AI security lab built around a fictional company. The company has customers, vendors, and internal policies, and the project is building one assistant to help people work with that data. The goal is to turn that setting into short, CTF-style exercises about document trust, access control, and agent tool permissions.
What’s implemented
Document ingestion. Extracts text from PDFs, Word documents, spreadsheets, CSVs, text files, and images. Uses OCR where needed and asks Qwen to normalize and classify the text.
Retrieval-augmented generation (RAG). Splits documents into overlapping chunks, embeds them with EmbeddingGemma, and stores them in Supabase. The Python helper `answer_question()` retrieves relevant chunks and returns a Qwen answer with source labels.
Company API and authentication. FastAPI exposes customer and vendor routes alongside Supabase Auth endpoints for registration, login, and logout. Several company read routes are placeholders.
`POST /agent/chat` is registered as a placeholder. Connecting it to retrieval, enforcing document access for each user, and adding the CTF-style challenges are planned.
Run locally
Install the Python dependencies in a virtual environment:
```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install fastapi uvicorn python-multipart python-dotenv supabase ollama numpy pymupdf easyocr python-docx openpyxl
   ```
Install and start Ollama, then download the two models:
```bash
   ollama pull qwen3.5:4b
   ollama pull embeddinggemma
   ```
Create a `.env` file next to `main.py` using your development Supabase project's URL and publishable key:
```dotenv
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-publishable-key
   ```
The API expects the corresponding Supabase tables and access policies to be configured separately. To try document ingestion, configure `document_chunks` to accept the `content`, `document_type`, and `embedding` values written by the Python helper, plus an `id` for each row so retrieval can identify its sources. Use synthetic records and documents for the lab.
Start FastAPI:
```bash
   python -m uvicorn main:app --reload
   ```
Open Swagger UI to inspect the registered routes.
Try document retrieval
Use a synthetic vendor policy PDF and call the helpers from the project directory:
```python
from main import answer_question, doc_vector_upload

doc_vector_upload("vendor-policy.pdf")
result = answer_question("How do I onboard a vendor?")
print(result["answer"])
print(result["sources"])
```
The query and document chunks use the same embedding model. The retriever sorts chunks by ascending cosine distance (`1 - cosine similarity`) and sends the top matches to Qwen as context.
First planned challenge
An employee and a customer ask the same vendor onboarding question. The employee should get an answer citing an internal policy they can read. The customer should receive an answer based on documents they can access. The challenge passes when the internal policy is filtered out before the customer's retrieved context reaches the model.
