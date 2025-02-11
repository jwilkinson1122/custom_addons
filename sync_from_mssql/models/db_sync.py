import pyodbc
import logging
import time
import datetime
from contextlib import contextmanager
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

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
    # ModifiedOn
    modified_stamp_field = fields.Char("Modified Timestamp Field")
    update_all = fields.Boolean("Update All", default=False)
    sync_all = fields.Boolean(
        "Sync All Records",
        help="If enabled, all records will be retrieved, not just modified ones.",
    )
    field_ids = fields.One2many(
        "base.db.sync.mssql.field", "dt_id", string="Field Mappings"
    )

    def action_show_details(self):
        """Opens a detailed field mapping form."""
        view = self.env.ref("sync_from_mssql.view_dbsync_field_tree")
        return {
            "name": "Field Mapping",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "base.db.sync.mssql.field",
            "view_id": view.id,
            "domain": [("dt_id", "=", self.id)],
            "target": "new",
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
        """Ensure `dt_id` is set when creating a new field mapping."""
        _logger.debug(f"Creating Field Mapping: {vals}")
        _logger.debug(f"Context at creation: {self.env.context}")

        # If dt_id is missing, try to get it from context or parent
        if not vals.get("dt_id"):
            if self.env.context.get("default_dt_id"):
                vals["dt_id"] = self.env.context["default_dt_id"]
                _logger.debug(f"Setting dt_id from default_dt_id: {vals['dt_id']}")
            elif self.env.context.get("active_id"):
                vals["dt_id"] = self.env.context["active_id"]
                _logger.debug(f"Setting dt_id from active_id: {vals['dt_id']}")
            else:
                # Fallback: Get the last used table mapping (Might not always be accurate)
                last_table = self.env["base.db.sync.mssql.table"].search([], limit=1)
                if last_table:
                    vals["dt_id"] = last_table.id
                    _logger.debug(
                        f"Setting dt_id from last table mapping: {vals['dt_id']}"
                    )

        if not vals.get("dt_id"):
            raise ValidationError(
                "Table Mapping (dt_id) is required for Field Mappings."
            )

        return super(DbSyncField, self).create(vals)

    @api.onchange("dt_id")
    def _onchange_dt_id(self):
        """Ensure `dt_id` is always set when adding a field mapping."""
        _logger.debug(
            f"Onchange Triggered: Context = {self.env.context}, dt_id = {self.dt_id}"
        )

        if not self.dt_id:
            if self.env.context.get("default_dt_id"):
                self.dt_id = self.env.context["default_dt_id"]
                _logger.debug(f"dt_id set from default_dt_id: {self.dt_id}")
            elif self.env.context.get("active_id"):
                self.dt_id = self.env.context["active_id"]
                _logger.debug(f"dt_id set from active_id: {self.dt_id}")


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
        """Fetch records based on user selection (modified only OR all records)."""

        # 🟢 Default to Jan 1, 2000 if no last sync date exists
        last_sync_date = self.last_updated or datetime.datetime(2000, 1, 1)
        formatted_date = last_sync_date.strftime("%Y-%m-%d %H:%M:%S")

        # ✅ Determine Query Based on Sync Mode
        if table.sync_all:
            query = f"SELECT * FROM {table.source_table}"  # Fetch all records
        else:
            if not table.modified_stamp_field:
                _logger.warning(
                    f"⚠️ Skipping {table.source_table}: No modified timestamp field set."
                )
                return

            query = f"""
                SELECT * FROM {table.source_table}
                WHERE {table.modified_stamp_field} >= '{formatted_date}'
            """

        _logger.debug(f"Executing query: {query}")  # ✅ Log SQL Query

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

        # ⚠️ Exit if No Records Found
        if not rows:
            _logger.info(f"⚠️ No records found in {table.source_table}, skipping sync.")
            return

        # ✅ Process records in batches
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
