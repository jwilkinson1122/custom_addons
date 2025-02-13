import pandas as pd
import phonenumbers
import re
import os
from datetime import datetime

# Set file paths
BASE_DIR = r"C:\odoo17\server\odoo\custom_addons\sync_from_mssql\data"
FILES = [
    "crm_all_active_accounts.csv",
    "crm_active_parent_accounts.csv",
    "crm_active_child_accounts.csv"
]

def clean_nulls(value):
    """Convert NULL, N/A, and empty strings to None."""
    return None if pd.isna(value) or value in ["NULL", "N/A", ""] else value.strip()

def clean_phone_number(phone):
    """Normalize phone numbers."""
    if pd.isna(phone) or not phone.strip():
        return None
    try:
        parsed = phonenumbers.parse(phone, "US")  # Change country if needed
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None
    return None

def clean_email(email):
    """Normalize email addresses."""
    if email and isinstance(email, str):
        email = email.strip().lower()
        return email if re.match(r"[^@]+@[^@]+\.[^@]+", email) else None
    return None

def fix_timestamp(timestamp):
    """Convert 'HH:MM.SS' format timestamps to 'YYYY-MM-DD HH:MM:SS'."""
    if not timestamp or pd.isna(timestamp):
        return None
    try:
        return datetime.strptime(timestamp, "%H:%M.%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None  # Invalid format

def clean_address(value):
    """Trim address fields."""
    return value.strip() if value and isinstance(value, str) else None

def clean_data(file_path):
    """Process and clean a CSV file."""
    try:
        df = pd.read_csv(file_path, dtype=str)  # Load as string to prevent data type issues
        print(f"Processing: {os.path.basename(file_path)}")

        # Strip spaces, replace NULLs
        df = df.applymap(clean_nulls)

        # Clean phone numbers
        phone_columns = ["address1_telephone1", "telephone1", "telephone2", "telephone3"]
        for col in phone_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_phone_number)

        # Clean emails
        email_columns = ["emailaddress1", "emailaddress2", "emailaddress3"]
        for col in email_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_email)

        # Fix timestamps
        if "modifiedon" in df.columns:
            df["modifiedon"] = df["modifiedon"].apply(fix_timestamp)

        # Clean address fields
        address_columns = ["address1_line1", "address1_line2", "address1_line3"]
        for col in address_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_address)

        # Remove empty rows
        df.dropna(how="all", inplace=True)

        # Save cleaned file
        cleaned_path = file_path.replace(".csv", "_cleaned.csv")
        df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
        print(f"✅ Cleaned file saved: {cleaned_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

if __name__ == "__main__":
    for file_name in FILES:
        file_path = os.path.join(BASE_DIR, file_name)
        if os.path.exists(file_path):
            clean_data(file_path)
        else:
            print(f"❌ File not found: {file_path}")
