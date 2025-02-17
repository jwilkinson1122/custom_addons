import os
import pymssql
import requests
import logging
import time
from retry import retry

# Configure Logging
logging.basicConfig(
    filename="/app/sync.log",  # Log file inside Docker container
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Environment Variables for Configurations
# MSSQL_HOST = os.getenv("MSSQL_SERVER", "mssql")
MSSQL_HOST = os.getenv("MSSQL_SERVER", "localhost")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "my_mssql_db")
MSSQL_USER = os.getenv("MSSQL_USER", "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "MyStrongMSSQLPass!")

ODOO_URL = os.getenv("ODOO_URL", "http://odoo:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

# Retry settings
MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds


@retry(tries=MAX_RETRIES, delay=RETRY_DELAY, backoff=2)
def connect_to_mssql():
    """Establish a connection to MSSQL with retry mechanism."""
    try:
        conn = pymssql.connect(
            server=MSSQL_HOST,
            user=MSSQL_USER,
            password=MSSQL_PASSWORD,
            database=MSSQL_DATABASE,
        )
        # conn = pymssql.connect(
        #     server="mssql",
        #     port="1433",
        #     user="sa",
        #     password="MyStrongMSSQLPass!",
        #     database="my_mssql_db",
        # )

        logging.info("✅ Connected to MSSQL successfully.")
        return conn
    except pymssql.DatabaseError as e:
        logging.error(f"❌ MSSQL Connection Error: {e}")
        raise


@retry(tries=MAX_RETRIES, delay=RETRY_DELAY, backoff=2)
def authenticate_odoo():
    """Authenticate with Odoo and return session ID."""
    auth_data = {
        "jsonrpc": "2.0",
        "params": {
            "db": ODOO_DB,
            "login": ODOO_USER,
            "password": ODOO_PASSWORD,
        },
    }

    response = requests.post(f"{ODOO_URL}/web/session/authenticate", json=auth_data)
    if response.status_code == 200 and response.json().get("result"):
        session_id = response.cookies.get("session_id")
        logging.info("✅ Authenticated with Odoo successfully.")
        return session_id
    else:
        logging.error(f"❌ Odoo Authentication Failed: {response.text}")
        raise Exception("Odoo authentication failed.")


def fetch_mssql_data():
    """Fetch data from MSSQL and handle exceptions."""
    try:
        conn = connect_to_mssql()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            "SELECT accountnumber, name, emailaddress1 FROM dbo.FilteredAccount WHERE statuscode = 1"
        )
        # cursor.execute(
        #     "SELECT accountnumber, accountname, emailaddress1 FROM my_mssql_db.dbo.FilteredAccount WHERE statuscode = 1"
        # )

        data = cursor.fetchall()
        conn.close()
        logging.info(f"✅ Fetched {len(data)} records from MSSQL.")
        return data
    except Exception as e:
        logging.error(f"❌ Error fetching data from MSSQL: {e}")
        return []


def sync_to_odoo():
    """Sync data from MSSQL to Odoo."""
    try:
        session_id = authenticate_odoo()
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"session_id={session_id}",
        }

        data = fetch_mssql_data()
        if not data:
            logging.warning("⚠️ No data to sync.")
            return

        for record in data:
            try:
                search_payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "res.partner",
                        "method": "search",
                        "args": [
                            [["legacy_customer_code", "=", record["accountnumber"]]]
                        ],
                    },
                }
                search_response = requests.post(
                    f"{ODOO_URL}/jsonrpc", json=search_payload, headers=headers
                )
                existing_partner = search_response.json().get("result", [])

                partner_data = {
                    "name": record["name"],
                    "email": record["emailaddress1"],
                    "legacy_customer_code": record["accountnumber"],
                }

                if existing_partner:
                    update_payload = {
                        "jsonrpc": "2.0",
                        "method": "call",
                        "params": {
                            "model": "res.partner",
                            "method": "write",
                            "args": [existing_partner, partner_data],
                        },
                    }
                    requests.post(
                        f"{ODOO_URL}/jsonrpc", json=update_payload, headers=headers
                    )
                    logging.info(f"🔄 Updated Partner: {record['name']}")

                else:
                    create_payload = {
                        "jsonrpc": "2.0",
                        "method": "call",
                        "params": {
                            "model": "res.partner",
                            "method": "create",
                            "args": [partner_data],
                        },
                    }
                    requests.post(
                        f"{ODOO_URL}/jsonrpc", json=create_payload, headers=headers
                    )
                    logging.info(f"✅ Created New Partner: {record['name']}")

            except Exception as e:
                logging.error(
                    f"❌ Error syncing record {record['accountnumber']} to Odoo: {e}"
                )

    except Exception as e:
        logging.critical(f"❌ Critical Sync Error: {e}")


if __name__ == "__main__":
    logging.info("🔄 Starting MSSQL-to-Odoo Sync...")
    sync_to_odoo()
    logging.info("✅ Sync Completed.")


