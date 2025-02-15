import pyodbc
import csv
import os
import logging
import time
import datetime
from contextlib import contextmanager
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ImportCRMAccounts(models.Model):
    _name = "crm.account.import"
    _description = "Import CRM Accounts from CSV"

    def _normalize_phone(self, phone):
        """Normalize phone number format"""
        return (
            phone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
            if phone
            else ""
        )

    def _normalize_email(self, email):
        """Convert email to lowercase"""
        return email.strip().lower() if email else ""

    def _get_state_id(self, state_name, country_code="US"):
        """Find or create state ID from name"""
        if not state_name:
            return False

        country = self.env["res.country"].search([("code", "=", country_code)], limit=1)
        if not country:
            return False  # Country not found

        state = self.env["res.country.state"].search(
            [("name", "=", state_name), ("country_id", "=", country.id)], limit=1
        )
        if not state:
            # Create missing state automatically
            state = self.env["res.country.state"].create(
                {
                    "name": state_name,
                    "code": state_name[:3].upper(),  # Generate a short code
                    "country_id": country.id,
                }
            )
            _logger.info(f"Created new state: {state.name} ({state.code})")

        return state.id

    def _get_country_id(self, country_name):
        """Get or create country ID from name"""
        if not country_name:
            return False

        country = self.env["res.country"].search([("name", "=", country_name)], limit=1)
        if not country:
            country = self.env["res.country"].create(
                {"name": country_name, "code": country_name[:2].upper()}
            )
            _logger.info(f"Created new country: {country.name} ({country.code})")

        return country.id

    def import_accounts(self, file_path, is_parent=True):
        """Import accounts from CSV"""
        if not os.path.exists(file_path):
            raise ValidationError(f"File not found: {file_path}")

        # Caching parent account mapping
        parent_mapping = {}

        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                account_number = row.get("accountnumber", "").strip()
                parent_account_id = row.get("parentaccountid", "").strip()

                if not account_number:
                    _logger.warning("Skipping row due to missing account number.")
                    continue  # Skip rows with no account number

                account_vals = {
                    "name": row.get("name", "").strip(),
                    "legacy_customer_code": account_number,
                    "street": row.get("address1_line1", "").strip(),
                    "street2": row.get("address1_line2", "").strip(),
                    "city": row.get("address1_city", "").strip(),
                    "state_id": self._get_state_id(
                        row.get("address1_stateorprovince", "").strip()
                    ),
                    "zip": row.get("address1_postalcode", "").strip(),
                    "country_id": self._get_country_id(
                        row.get("address1_country", "").strip()
                    ),
                    "phone": self._normalize_phone(row.get("address1_telephone1")),
                    "email": self._normalize_email(row.get("emailaddress1")),
                    "website": row.get("websiteurl", "").strip(),
                    "is_company": True,
                    "is_account": is_parent,
                    "is_affiliate": not is_parent,
                }

                # Cache parent accounts
                if is_parent:
                    parent_mapping[account_number] = None  # Initialize parent cache

                # Handle parent linking if this is a child account
                if not is_parent and parent_account_id:
                    parent = parent_mapping.get(parent_account_id)
                    if not parent:
                        parent = self.env["res.partner"].search(
                            [("legacy_customer_code", "=", parent_account_id)], limit=1
                        )
                        if parent:
                            parent_mapping[parent_account_id] = parent.id
                    if parent:
                        account_vals["parent_id"] = parent.id

                # Check if account already exists
                existing_partner = self.env["res.partner"].search(
                    [("legacy_customer_code", "=", account_number)], limit=1
                )

                if existing_partner:
                    existing_partner.write(account_vals)
                    _logger.info(f"Updated Partner: {existing_partner.name}")
                else:
                    new_partner = self.env["res.partner"].create(account_vals)
                    _logger.info(f"Created New Partner: {new_partner.name}")

        _logger.info("Import completed.")


class Partner(models.Model):
    _inherit = "res.partner"

    legacy_customer_code = fields.Char(
        string="Legacy Customer Code", index=True, help="Stores old CRM account number"
    )

    # search parent accounts using their GUID when importing child accounts.
    sql_guid = fields.Char(
        string="SQL GUID",
        index=True,
        help="Stores the GUID from SQL data for reference",
    )

    @api.model
    def _get_state_id(self, state_code, country_code="US"):
        """Find or create the state based on state code."""
        if not state_code:
            return False  # Return None if no state is provided

        country = self.env["res.country"].search([("code", "=", country_code)], limit=1)
        if not country:
            return False  # No country found

        state = self.env["res.country.state"].search(
            [("code", "=", state_code.upper()), ("country_id", "=", country.id)],
            limit=1,
        )

        if not state:
            # Optionally create the state if it doesn't exist
            state = self.env["res.country.state"].create(
                {
                    "name": state_code.upper(),  # Use the state code as a name if no full name is available
                    "code": state_code.upper(),
                    "country_id": country.id,
                }
            )
            _logger.info(f"Created new state: {state.name} ({state.code})")

        return state.id

    def import_parent_accounts(self, file_path):
        """Import Parent Accounts"""
        self.env["crm.account.import"].import_accounts(file_path, is_parent=True)

    def import_child_accounts(self, file_path):
        """Import Child Accounts and Link to Parent"""
        self.env["crm.account.import"].import_accounts(file_path, is_parent=False)


class OutDbSource(models.Model):
    _name = "base.db.source"
    _description = "External DB Source"
    _rec_name = "source_name"

    source_name = fields.Char(string="Source Name", required=True, unique=True)
    source_host = fields.Char(string="Source Host", required=True)
    source_db_name = fields.Char(string="Source Database", required=True)
    source_user_id = fields.Char(string="Source User ID", required=True)
    source_password = fields.Char(string="Source Password", required=True)
    state = fields.Boolean("State")

    # def connect_sql_server(self):
    #     """Establishes a connection to SQL Server."""
    #     try:
    #         return pyodbc.connect(
    #             f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};"
    #             f"UID={self.sql_user};PWD={self.sql_user_password};Trusted_Connection=no;"
    #         )
    #     except Exception as e:
    #         _logger.error("Failed to connect to SQL Server for %s: %s", self.name, e)
    #         return None

    @contextmanager
    def get_connection(self):
        """Context manager for handling MSSQL database connections"""
        conn = None  # Ensure connection variable is always defined
        try:
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={self.source_host},1433;DATABASE={self.source_db_name};"
                f"UID={self.source_user_id};PWD={self.source_password}"
            )
            conn = pyodbc.connect(conn_str, autocommit=True)
            yield conn
        except Exception as e:
            _logger.error(f"Database connection failed: {e}")
            raise ValidationError(f"Connection test failed: {tools.ustr(e)}")
        finally:
            if conn:
                conn.close()

    def test_connection(self):
        """Tests the database connection and displays a success or failure message."""
        try:
            with self.get_connection():
                pass
            self.state = True
            return {
                "name": "Success",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "message.wizard",
                "target": "new",
                "context": {"default_message": "Connection successful!"},
            }
        except ValidationError as e:
            return {
                "name": "Connection Failed",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "message.wizard",
                "target": "new",
                "context": {"default_message": f"Connection failed: {e}"},
            }


class DbSyncField(models.Model):
    _name = "base.db.sync.mssql.field"
    _description = "Database Sync Field Mapping"
    _order = "sequence, id"

    dt_id = fields.Many2one(
        "base.db.sync.mssql.table",
        string="Table Mapping",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    source_field = fields.Char("Source Field", required=True)
    destination_field = fields.Many2one(
        "ir.model.fields", string="Destination Field", required=True, ondelete="cascade"
    )
    is_pk = fields.Boolean("Primary Key")

    @api.model
    def create(self, vals):
        """Ensure dt_id is always set when creating a new field mapping."""
        _logger.debug(f"🔍 Creating Field Mapping with values: {vals}")
        _logger.debug(f"🔍 Context at creation: {self.env.context}")

        if not vals.get("dt_id"):
            context_dt_id = self.env.context.get("default_dt_id")
            active_id = self.env.context.get("active_id")

            if context_dt_id:
                vals["dt_id"] = context_dt_id
                _logger.debug(f"✅ Setting dt_id from default_dt_id: {context_dt_id}")
            elif active_id:
                vals["dt_id"] = active_id
                _logger.debug(f"✅ Setting dt_id from active_id: {active_id}")
            else:
                last_table = self.env["base.db.sync.mssql.table"].search([], limit=1)
                if last_table:
                    vals["dt_id"] = last_table.id
                    _logger.debug(
                        f"✅ Setting dt_id from last table mapping: {last_table.id}"
                    )
                else:
                    _logger.error("🚨 dt_id is missing! Cannot proceed.")
                    raise ValidationError(
                        "Table Mapping (dt_id) is required for Field Mappings."
                    )

        _logger.info(f"✅ Final dt_id used: {vals.get('dt_id')}")
        record = super().create(vals)
        _logger.info(f"✅ Successfully created Field Mapping: {record.id}")
        return record

    @api.onchange("dt_id")
    def _onchange_dt_id(self):
        """Ensure `dt_id` is always set when adding a field mapping."""
        _logger.debug(
            f"🛠 Onchange Triggered: Context = {self.env.context}, dt_id = {self.dt_id}"
        )
        if not self.dt_id:
            if self.env.context.get("default_dt_id"):
                self.dt_id = self.env.context["default_dt_id"]
                _logger.debug(f"🛠 dt_id set from default_dt_id: {self.dt_id}")
            elif self.env.context.get("active_id"):
                self.dt_id = self.env.context["active_id"]
                _logger.debug(f"🛠 dt_id set from active_id: {self.dt_id}")


class DbSyncTable(models.Model):
    _name = "base.db.sync.mssql.table"
    _description = "Database Sync Table Mapping"

    ds_id = fields.Many2one(
        "base.db.sync.mssql",
        string="Database Sync Reference",
        required=True,
        ondelete="cascade",
    )
    source_table = fields.Char(string="Source Table", required=True)
    destination_model = fields.Many2one(
        "ir.model", string="Destination Model", required=True, ondelete="cascade"
    )
    modified_stamp_field = fields.Char("Modified Timestamp Field")
    update_all = fields.Boolean("Update All", default=False)
    # sync_all = fields.Boolean("Sync All Records", help="If enabled, all records will be retrieved, not just modified ones.")
    sync_all = fields.Boolean(
        "Sync All Records",
        default=False,
        help="If enabled, all records will be retrieved, not just modified ones.",
    )
    selected_columns = fields.Text(
        string="Selected Columns",
        help="Comma-separated column names to fetch. Leave blank for all columns.",
    )
    custom_row_filter = fields.Text(
        string="Custom Row Filter",
        help="Custom SQL WHERE clause to filter rows. Example: 'Status = Active'",
    )
    field_ids = fields.One2many(
        "base.db.sync.mssql.field", "dt_id", string="Field Mappings"
    )

    def action_show_details(self):
        """Opens a detailed field mapping form."""
        view = self.env.ref("sync_from_mssql.view_db_sync_field_tree")
        return {
            "name": "Field Mapping",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "base.db.sync.mssql.field",
            "view_id": view.id,
            "domain": [("dt_id", "=", self.id)],
            "target": "new",
        }

    @api.model
    def create(self, vals):
        """Ensure ds_id is always set when creating a new table mapping."""
        _logger.debug(f"🔍 Creating Table Mapping with values: {vals}")
        _logger.debug(f"🔍 Context at creation: {self.env.context}")

        if not vals.get("ds_id"):
            context_ds_id = self.env.context.get("default_ds_id")
            active_id = self.env.context.get("active_id")

            if context_ds_id:
                vals["ds_id"] = context_ds_id
                _logger.debug(f"✅ Setting ds_id from default_ds_id: {context_ds_id}")
            elif active_id:
                vals["ds_id"] = active_id
                _logger.debug(f"✅ Setting ds_id from active_id: {active_id}")
            else:
                last_sync = self.env["base.db.sync.mssql"].search([], limit=1)
                if last_sync:
                    vals["ds_id"] = last_sync.id
                    _logger.debug(f"✅ Setting ds_id from last sync: {last_sync.id}")
                else:
                    _logger.error("🚨 ds_id is missing! Cannot proceed.")
                    raise ValidationError(
                        "Sync Reference (ds_id) is required for Table Mappings."
                    )

        _logger.info(f"✅ Final ds_id used: {vals.get('ds_id')}")
        record = super().create(vals)
        _logger.info(f"✅ Successfully created Table Mapping: {record.id}")
        return record


class DbSync(models.Model):
    _name = "base.db.sync.mssql"
    _description = "Sync From MSSQL"

    sync_name = fields.Char(string="Sync Name", required=True)
    source = fields.Many2one("base.db.source", string="Database Source", required=True)
    last_updated = fields.Datetime("Last Updated")
    table_ids = fields.One2many("base.db.sync.mssql.table", "ds_id", copy=True)
    sync_logs = fields.Text("Sync Logs")
    active = fields.Boolean("Active", default=True)

    def process_sync(self):
        """Send an email alert if multiple sync failures occur"""
        start_time = time.time()
        errors = []

        try:
            with self.source.get_connection() as conn:
                for table in self.table_ids:
                    try:
                        self.sync_table(conn, table)
                    except Exception as e:
                        error_msg = f"Table {table.source_table}: {str(e)}"
                        errors.append(error_msg)

                        # ✅ Use `DbSyncLog` instead of `self.log_error`
                        self.env["base.db.sync.log"].create(
                            {
                                "sync_id": self.id,
                                "log_type": "error",
                                "message": error_msg,
                            }
                        )

                        _logger.error(error_msg)

            self.last_updated = datetime.now()
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            errors.append(error_msg)

            # ✅ Use `DbSyncLog` instead of `self.log_error`
            self.env["base.db.sync.log"].create(
                {
                    "sync_id": self.id,
                    "log_type": "error",
                    "message": error_msg,
                }
            )

            _logger.error(error_msg)

        elapsed_time = time.time() - start_time
        success_msg = f"Sync completed in {elapsed_time:.2f} seconds"
        self.append_log(success_msg)
        _logger.info(success_msg)

        if errors:
            # self.send_failure_email(errors)
            return self.show_error_message(errors)

    def action_resync_all(self):
        """Force a full re-sync for all tables."""
        self.ensure_one()
        for table in self.table_ids:
            table.sync_all = True  # ✅ Enable full sync
        return self.process_sync()

    def show_error_message(self, errors):
        """Displays error messages in Odoo UI"""
        error_text = "\n".join(errors)
        return {
            "name": "Sync Errors",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "message.wizard",
            "target": "new",
            "context": {"default_message": error_text},
        }

    def sync_table(self, conn, table):
        """Fetch records based on user selection: Partial Column & Row Sync."""

        last_sync_date = self.last_updated or datetime.datetime(2000, 1, 1)
        formatted_date = last_sync_date.strftime("%Y-%m-%d %H:%M:%S")

        # 🟢 Select specific columns if set
        if table.selected_columns:
            column_list = table.selected_columns.replace(" ", "").split(",")
            column_query = ", ".join(column_list)
        else:
            column_query = "*"

        # 🟢 Build WHERE conditions
        where_conditions = []
        if not table.sync_all:
            if not table.modified_stamp_field:
                _logger.warning(
                    f"⚠️ Skipping {table.source_table}: No modified timestamp field set."
                )
                return
            where_conditions.append(
                f"{table.modified_stamp_field} >= '{formatted_date}'"
            )

        if table.custom_row_filter:
            where_conditions.append(table.custom_row_filter)

        where_clause = (
            f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        )

        # ✅ Construct Query
        query = f"SELECT {column_query} FROM {table.source_table} {where_clause}"

        _logger.debug(f"Executing query: {query}")

        cursor = conn.cursor()
        try:
            cursor.execute(query)
            columns = [
                column[0] for column in cursor.description
            ]  # ✅ Get column names
            rows = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]  # ✅ Convert to dicts
            _logger.info(f"✅ Retrieved {len(rows)} records from {table.source_table}.")
        except pyodbc.ProgrammingError as e:
            _logger.error(f"❌ SQL Query Failed: {query}")
            _logger.error(f"SQL Error: {str(e)}")
            raise ValidationError(f"SQL Query Failed: {str(e)}")

        if not rows:
            _logger.info(f"⚠️ No records found in {table.source_table}, skipping sync.")
            return

        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            self.update_odoo_model(table, batch)

    def update_odoo_model(self, table, rows):
        """Insert or update records in Odoo models (single or batch processing)."""
        model = self.env[table.destination_model.model]
        bulk_create_data = []
        bulk_update_data = []

        # Ensure `rows` is always iterable (single record compatibility)
        if not isinstance(rows, list):
            rows = [rows]

        for row in rows:
            values = {}

            for field in table.field_ids:
                source_field = field.source_field

                # ✅ Handle both dictionary-based and index-based row retrieval
                source_value = row.get(source_field) if isinstance(row, dict) else None

                # Handle State Mapping
                if field.destination_field.name == "state_id":
                    values["state_id"] = self.env["res.partner"]._get_state_id(
                        source_value
                    )
                else:
                    values[field.destination_field.name] = source_value

            # Ensure record uniqueness using Primary Key
            domain = [
                (field.destination_field.name, "=", row[field.source_field])
                for field in table.field_ids
                if field.is_pk
            ]

            existing_record = model.search(domain, limit=1)

            if existing_record:
                bulk_update_data.append((existing_record, values))
            else:
                bulk_create_data.append(values)

        # ✅ Perform bulk inserts for better performance
        if bulk_create_data:
            model.create(bulk_create_data)
            _logger.info(
                f"Inserted {len(bulk_create_data)} new records into {table.destination_model.model}"
            )

        # ✅ Perform batch updates efficiently
        if bulk_update_data:
            for rec, vals in bulk_update_data:
                rec.write(vals)
            _logger.info(
                f"Updated {len(bulk_update_data)} records in {table.destination_model.model}"
            )

    def append_log(self, message):
        """Appends log messages to sync_logs"""
        self.sync_logs = f"{self.sync_logs or ''}\n[{datetime.now()}] {message}"

    # def send_failure_email(self, errors):
    #     """Send an email notification if a sync failure occurs multiple times"""
    #     template = self.env.ref("sync_from_mssql.email_template_sync_failure", raise_if_not_found=False)
    #     if template:
    #         template.sudo().send_mail(self.id, force_send=True)
    #         _logger.info(f"Sync failure email sent for {self.sync_name}")
    #     else:
    #         _logger.warning("Email template for sync failure not found.")

    # def send_failure_email(self, errors):
    #     """Send an email notification if a sync failure occurs multiple times"""
    #     template = self.env.ref("sync_mssql.email_template_sync_failure")
    #     if template:
    #         template.sudo().send_mail(self.id, force_send=True)


class DbSyncLog(models.Model):
    _name = "base.db.sync.log"
    _description = "Database Sync Log"

    sync_id = fields.Many2one(
        "base.db.sync.mssql", string="Sync Reference", required=True, ondelete="cascade"
    )
    log_type = fields.Selection(
        [("info", "Info"), ("error", "Error")], string="Log Type", required=True
    )
    message = fields.Text("Log Message", required=True)
    log_time = fields.Datetime("Log Time", default=fields.Datetime.now, required=True)

    def log_error(self, message):
        """Logs errors in the sync log table"""
        self.env["base.db.sync.log"].create(
            {
                "sync_id": self.id,
                "log_type": "error",
                "message": message,
            }
        )
