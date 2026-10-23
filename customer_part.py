import os
import tempfile
from pathlib import Path
from datetime import date
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, UploadFile
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
    os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"),
)

router = APIRouter(prefix="/router",tags=["Customer"])


@router.post("/customer")
def save_customer(
    f_name: str = Form(...),
    l_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    home_address: str = Form(...),
    birth_date: date = Form(...),
):
    """save customer information to the customers table."""
    result = supabase.table("customers").insert({
        "f_name": f_name,
        "l_name": l_name,
        "email": email,
        "phone_number": phone_number,
        "home_address": home_address,
        "birth_date": birth_date.isoformat(),
    }).execute()

    return result.data


@router.post("/customer/{customer_id}/bank-details")
def save_bank_details(
    customer_id: str,
    bank_name: str = Form(...),
    account_type: str = Form("checking"),
    account_number: str = Form(...),
    routing_number: str = Form(...),
    is_primary: bool = Form(False),
):
    """save bank information to the customer_bank_details table."""
    result = supabase.table("customer_bank_details").insert({
        "customer_id": customer_id,
        "bank_name": bank_name,
        "account_type": account_type,
        "account_number_last_four": account_number[-4:],
        "is_primary": is_primary,
        "status": "active",
    }).execute()

    return result.data


@router.post("/customer/{customer_id}/bank-statements")
async def parse_and_save_statement(
    customer_id: str,
    file: UploadFile = File(...),
    bank_name: str = Form(...),
    statement_period_start: date = Form(...),
    statement_period_end: date = Form(...),
    account_number_last_four: Optional[str] = Form(None),
    opening_balance: Optional[float] = Form(None),
    closing_balance: Optional[float] = Form(None),
    total_deposits: Optional[float] = Form(None),
    total_withdrawals: Optional[float] = Form(None),
):
    """parse PDF/CSV/XLSX and store in bank_statements table."""
    from main import parse_document

    suffix = Path(file.filename or "statement").suffix.lower()
    data = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(data)
        temp_path = temp.name

    try:
        extracted_text = parse_document(temp_path)
    finally:
        os.remove(temp_path)

    result = supabase.table("bank_statements").insert({
        "customer_id": customer_id,
        "bank_name": bank_name,
        "account_number_last_four": account_number_last_four,
        "statement_period_start": statement_period_start.isoformat(),
        "statement_period_end": statement_period_end.isoformat(),
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "total_deposits": total_deposits or 0,
        "total_withdrawals": total_withdrawals or 0,
        "currency": "USD",
        "raw_text": extracted_text,
        "metadata": {
            "original_filename": file.filename,
            "content_type": file.content_type,
        },
    }).execute()

    return {
        "saved": result.data,
        "extracted_text": extracted_text,
    }


@router.get("/customer/{customer_id}/bank-statements")
def get_bank_statements(customer_id: str):
    """get a list of statements for the specified customer."""
    result = (
        supabase.table("bank_statements")
        .select("*")
        .eq("customer_id", customer_id)
        .execute()
    )
    return result.data