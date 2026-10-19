import csv  # CSV parsing is included in Python's standard library.

import easyocr  # Read text from images when OCR is needed.
import ollama  # Call a Qwen model through Ollama when the agent is implemented.
from docx import Document  # Read DOCX documents (python-docx package).
from fastapi import FastAPI
from openpyxl import load_workbook  # Read XLSX spreadsheets.
from pypdf import PdfReader  # Read text from PDF documents.
from supabase import Client, create_client  # Connect to Supabase when configured.


app = FastAPI(title="Dummy Company Commerce API")

# Supabase will provide storage. Client setup will be added once configured.
# Parser imports are ready for later use; no files are processed at startup.
# AUTHENTICATION
@app.post("/auth", tags=["Authentication"])
def authenticate():
    # TODO: Define the authentication inputs and behavior.
    pass


# CUSTOMER
@app.get("/customer", tags=["Customer"])
def get_customer():
    # TODO: Define which customer information this route returns.
    pass


# COMPANY
@app.get("/company/vendors", tags=["Company"])
def get_company_vendors():
    # TODO: Retrieve company vendor data from Supabase.
    pass


@app.get("/company/customers", tags=["Company"])
def get_company_customers():
    # TODO: Retrieve the company's customer information from Supabase.
    pass


@app.get("/company/legal-documents", tags=["Company"])
def get_company_legal_documents():
    # TODO: Retrieve the company's legal documents from Supabase.
    pass


@app.get("/company/policies", tags=["Company"])
def get_company_policies():
    # TODO: Retrieve the company's policies from Supabase.
    pass


# AGENT
@app.post("/agent/chat", tags=["Agent"])
def agent_chat():
    # TODO: Define chat inputs and connect to a Qwen model through Ollama.
    pass