# -*- coding: utf-8 -*-
import re
import ast
import base64
import json
from odoo import api, fields, models, _
import pyodbc
from odoo.exceptions import UserError
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

ACCEPTED_FIELDS = {
    "many2many",
    "one2many",
    "many2one_reference",
    "datetime",
    "monetary",
    "html",
    "date",
    "selection",
    "many2one",
    "float",
    "reference",
    "boolean",
    "char",
    "text",
    "integer",
    "binary",
}


class SqlIntegration(models.Model):
    _name = "sql.integration"
    _description = "SQL Integration"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    server = fields.Char(required=True)
    database = fields.Char(required=True)
    sql_user = fields.Char(required=True)
    sql_user_password = fields.Char(required=True)
    query = fields.Text()
    res_model_id = fields.Many2one("ir.model", string="Model", ondelete="cascade")
    model_name = fields.Char(related="res_model_id.model", readonly=True, store=True)
    filter_domain = fields.Char()
    query_result = fields.Html(copy=False)
    action_type = fields.Selection(
        [
            ("create", "Create"),
            ("create_not_exist", "Create if not exist"),
            ("update", "Update"),
            ("update_create_not_exist", "Update & Create if not exist"),
        ],
        default="create",
    )
    integration_fields = fields.One2many(
        "sql.integration.line", "integration_id", required=True
    )
    ready = fields.Boolean(copy=False)
    enable_automation = fields.Boolean("Enable")
    next_call = fields.Datetime()
    last_call = fields.Datetime("Last executed on")
    interval_number = fields.Integer(default=1)
    interval_unit = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        default="days",
    )

    def make_it_ready(self):
        """Validates integration setup and prepares it for execution."""
        self.ensure_one()
        if not self.res_model_id:
            raise UserError(_("Please choose a Model!"))
        if not self.action_type:
            raise UserError(_("Please select an Action Type!"))
        if not self.integration_fields:
            raise UserError(_("Please map fields to integrate data!"))

        cnxn = self.connect_sql_server()
        if not cnxn:
            raise UserError(_("Error connecting to SQL Server!"))

        self.run_query()
        self.ready = True

    @api.onchange("query")
    def _onchange_query(self):
        """Resets query results when query is changed."""
        self.query_result = False
        self.ready = False

    @api.onchange("enable_automation")
    def _onchange_enable_automation(self):
        """Sets next execution time when automation is enabled."""
        if self.enable_automation:
            self.next_call = fields.Datetime.now()

    def run_query(self):
        """Executes SQL query and generates an HTML table preview."""
        self.ensure_one()
        if not self.query.upper().startswith("SELECT"):
            raise UserError(_('Invalid Query! Query should start with "SELECT".'))

        query = f"SELECT TOP 3 * FROM ({self.query}) e"
        data = self.fetch_data_from_sql(col=True, query=query)

        if not data.get("column"):
            raise UserError(_("No data returned from the query!"))

        headers = "".join(
            f'<th style="border:1px solid black;padding:5px;background:#999;color:#fff">[{idx}] {col}</th>'
            for idx, col in enumerate(data["column"])
        )

        rows = "".join(
            "<tr>"
            + "".join(
                f'<td style="border:1px solid black;padding:3px;">{d[idx]}</td>'
                for idx in range(len(data["column"]))
            )
            + "</tr>"
            for d in data["datas"]
        )

        self.query_result = (
            f'<table style="width:100%;"><tr>{headers}</tr>{rows}</table>'
        )

    def _get_unique_record(self, domain_filter):
        """Fetches a unique record based on the provided domain filter."""
        return self.env[self.model_name].search(domain_filter, limit=1)

    ### 🛠️ HELPER METHODS ###
    def _get_index_value(self, field, data):
        """Retrieve and validate field index from data list."""
        try:
            index = int(field.value) if field.value.lstrip("-").isdigit() else None
        except ValueError:
            index = None

        if index is None or index < 0 or index >= len(data):
            _logger.warning(
                f"Skipping {field.res_field_id.name}: Index {index} is invalid or out of range (data length={len(data)})"
            )
            return None
        return data[index]

    def _find_state_id(self, state_code):
        """Find and return the state_id based on the provided state code."""
        if not state_code or not isinstance(state_code, str):
            _logger.warning("Skipping state_id: Empty or invalid state code")
            return None

        state_code = state_code.strip().upper()  # ✅ Standardize formatting
        _logger.debug(f"Looking up state_id for code: '{state_code}'")

        state_record = self.env["res.country.state"].search(
            [("code", "=", state_code)], limit=1
        )

        if state_record:
            _logger.debug(
                f"Matched state_id: {state_record.id} for code '{state_code}'"
            )
            return state_record.id

        _logger.warning(f"Skipping state_id: No state found for code '{state_code}'")
        return None

    def _find_related_record(self, field, lookup_value):
        """Perform a generic dynamic lookup for many2one fields."""
        if not field.value_domain:
            _logger.warning(
                f"Skipping {field.res_field_id.name}: No value_domain provided."
            )
            return None

        search_field = field.value_domain[0][0]
        related_model = self.env[field.res_field_id.relation]

        _logger.debug(
            f"Searching {related_model._name} for {search_field} = '{lookup_value}'"
        )

        related_record = related_model.search(
            [(search_field, "=", lookup_value)], limit=1
        )

        if related_record:
            _logger.debug(
                f"Found match: {related_record.id} for {search_field} = '{lookup_value}'"
            )
            return related_record.id

        _logger.warning(
            f"Skipping {field.res_field_id.name}: No match found for {search_field} = '{lookup_value}'"
        )
        return None

    def _get_val_dict(self, method, data=None):
        """Constructs a dictionary of values for integration fields dynamically."""
        if not isinstance(data, (list, tuple)):
            _logger.warning(f"Expected list/tuple, got {type(data)}: {data}")
            return {}

        _logger.debug(f"Received data: {data}")
        val_dict = {}

        for field in self.integration_fields:
            if method == field.exclude:
                continue  # Skip excluded fields

            field_name = field.res_field_id.name
            _logger.debug(f"Processing field: {field_name}, field.value: {field.value}")

            value = self._get_index_value(field, data)
            if value is None:
                continue  # Skip if index is invalid

            if isinstance(value, str):
                value = value.strip()

            if value in [None, ""]:
                _logger.warning(f"Skipping {field_name}: Value is empty or None")
                continue  # Do not add it to val_dict

            if field.evaluation_type == "seq":
                val_dict[field_name] = value

            elif (
                field.res_field_id.ttype == "binary" and field.evaluation_type == "seq"
            ):
                val_dict[field_name] = (
                    base64.b64encode(value).decode()
                    if isinstance(value, bytes)
                    else None
                )

            elif field.evaluation_type == "value":
                val_dict[field_name] = field.value

            # elif field.evaluation_type == "find":
            #     if field_name == "state_id":
            #         if len(data) > 3 and data[3]:
            #             state_id = self._find_state_id(data[3].strip())
            #             if state_id:
            #                 val_dict[field_name] = state_id
            #             else:
            #                 _logger.warning(
            #                     f"Skipping state_id: No match for '{data[3]}'"
            #                 )
            #         else:
            #             _logger.warning(
            #                 f"Skipping state_id: Missing or invalid data[3] ({data})"
            #             )
            #     else:
            #         val_dict[field_name] = self._find_related_record(field, value)

            elif field.evaluation_type == "find":
                if field_name == "state_id":
                    if (
                        isinstance(value, str) and value.strip()
                    ):  # Ensure we have a string
                        state_id = self._find_state_id(
                            value.strip()
                        )  # Use correct value lookup
                        if state_id:
                            val_dict[field_name] = state_id
                        else:
                            _logger.warning(
                                f"Skipping state_id: No match for '{value}'"
                            )
                    else:
                        _logger.warning(
                            f"Skipping state_id: Missing or invalid state code '{value}'"
                        )
                else:
                    val_dict[field_name] = self._find_related_record(field, value)

        # ✅ Move validation **after** processing fields
        if "city" in val_dict and not val_dict["city"]:
            _logger.warning("Skipping record: Missing 'city' field.")
            return {}

        if "state_id" in val_dict and not val_dict["state_id"]:
            _logger.warning("Skipping record: Missing 'state_id' field.")
            return {}

        _logger.debug(f"Final generated values: {val_dict}")
        return val_dict

    def _get_val_string(self, method, data=None):
        """Ensures that the function returns a proper dictionary, not a JSON string."""
        val_dict = self._get_val_dict(method, data)
        if not isinstance(val_dict, dict):  # Ensure it's a dictionary
            _logger.error(f"_get_val_string expected dict, got {type(val_dict)}")
            return {}
        return val_dict  # Return dictionary, NOT json.dumps(val_dict)

    ### 🔄 PROCESS RECORD ###
    def process_record(self, data):
        """Processes a single record, ensuring that existing records are updated and new ones are created safely."""
        val_dict = self._get_val_dict(self.action_type, data)
        if not val_dict:
            _logger.warning("Skipping record: No valid data extracted")
            return

        legacy_code = val_dict.get("legacy_customer_code")
        if not legacy_code:
            _logger.warning("Skipping record: Missing legacy_customer_code")
            return

        domain = [("legacy_customer_code", "=", legacy_code)]
        existing_records = self.env[self.model_name].search(domain)

        # ✅ Ensure only one record is updated
        if len(existing_records) > 1:
            _logger.warning(
                f"Duplicate legacy_customer_code found for '{legacy_code}', skipping update."
            )
            return

        # ✅ Remove 'False' values from val_dict before writing
        val_dict = {k: v for k, v in val_dict.items() if v is not False}

        if self.action_type in ["create", "create_not_exist"]:
            if existing_records:
                _logger.warning(
                    f"Skipping create: Record with legacy_customer_code '{legacy_code}' already exists"
                )
            else:
                val_dict.setdefault(
                    "customer_code",
                    self.env["ir.sequence"].next_by_code("customer.company.code")
                    or _("New"),
                )
                _logger.debug(f"Creating new record: {val_dict}")
                self.env[self.model_name].create(val_dict)

        elif self.action_type in ["update", "update_create_not_exist"]:
            if existing_records:
                _logger.debug(
                    f"Updating existing record ID {existing_records.id}: {val_dict}"
                )
                existing_records.write(val_dict)
            elif self.action_type == "update_create_not_exist":
                val_dict.setdefault(
                    "customer_code",
                    self.env["ir.sequence"].next_by_code("customer.company.code")
                    or _("New"),
                )
                _logger.debug(f"Creating new record: {val_dict}")
                self.env[self.model_name].create(val_dict)
            else:
                _logger.warning(
                    f"Skipping update: No existing record found for legacy_customer_code '{legacy_code}'"
                )

    # def process_record(self, data):
    #     """Processes a single record, ensuring that existing records are updated and new ones are created safely."""
    #     val_dict = self._get_val_dict(self.action_type, data)
    #     if not val_dict:
    #         _logger.warning("Skipping record: No valid data extracted")
    #         return

    #     legacy_code = val_dict.get("legacy_customer_code")
    #     if not legacy_code:
    #         _logger.warning("Skipping record: Missing legacy_customer_code")
    #         return

    #     domain = [("legacy_customer_code", "=", legacy_code)]
    #     existing_record = self.env[self.model_name].search(domain, limit=1)

    #     val_dict = {k: v for k, v in val_dict.items() if v is not False}

    #     if self.action_type in ["create", "create_not_exist"]:
    #         if existing_record:
    #             _logger.warning(
    #                 f"Skipping create: Record with legacy_customer_code '{legacy_code}' already exists"
    #             )
    #         else:
    #             val_dict.setdefault(
    #                 "customer_code",
    #                 self.env["ir.sequence"].next_by_code("customer.company.code")
    #                 or _("New"),
    #             )
    #             _logger.debug(f"Creating new record: {val_dict}")
    #             self.env[self.model_name].create(val_dict)

    #     elif self.action_type in ["update", "update_create_not_exist"]:
    #         if existing_record:
    #             _logger.debug(
    #                 f"Updating existing record ID {existing_record.id}: {val_dict}"
    #             )
    #             existing_record.write(val_dict)
    #         elif self.action_type == "update_create_not_exist":
    #             val_dict.setdefault(
    #                 "customer_code",
    #                 self.env["ir.sequence"].next_by_code("customer.company.code")
    #                 or _("New"),
    #             )
    #             _logger.debug(f"Creating new record: {val_dict}")
    #             self.env[self.model_name].create(val_dict)
    #         else:
    #             _logger.warning(
    #                 f"Skipping update: No existing record found for legacy_customer_code '{legacy_code}'"
    #             )

    def run_now(self):
        """Executes the integration process with detailed debugging."""
        datas = self.fetch_data_from_sql()
        if not datas:
            _logger.warning("No data retrieved from SQL Server.")
            return

        for data in datas["datas"]:
            _logger.debug(f"Processing data: {data}")

            try:
                with self.env.cr.savepoint():
                    vals = self._get_val_string(
                        "create" if self.action_type.startswith("create") else "update",
                        data,
                    )
                    _logger.debug(f"Generated values: {vals}")

                    domain = eval(self.filter_domain) if self.filter_domain else []
                    unique = self._get_unique_record(domain)

                    if self.action_type == "create" or (
                        self.action_type == "create_not_exist" and not unique
                    ):
                        self.env[self.model_name].create(vals)
                    elif self.action_type == "update" and unique:
                        unique.write(vals)
                    elif self.action_type == "update_create_not_exist":
                        if unique:
                            unique.write(vals)
                        else:
                            self.env[self.model_name].create(vals)
            except Exception as e:
                _logger.warning(
                    f"Exception in SQL Integration {self.name}: {e} (data={data})"
                )

        self.last_call = fields.Datetime.now()

    ### ⏰ AUTOMATION ###
    def cron_auto_execution(self):
        """Automated execution of integrations based on scheduling."""
        now = fields.Datetime.now()
        records = self.search(
            [("enable_automation", "=", True), ("next_call", "<=", now)]
        )
        for rec in records:
            rec.run_now()
            rec.next_call += relativedelta(**{rec.interval_unit: rec.interval_number})

    def connect_sql_server(self):
        """Establishes a connection to SQL Server."""
        try:
            return pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};"
                f"UID={self.sql_user};PWD={self.sql_user_password};Trusted_Connection=no;"
            )
        except Exception as e:
            _logger.error("Failed to connect to SQL Server for %s: %s", self.name, e)
            return None

    def test_sql_connection(self):
        cnxn = self.connect_sql_server()
        if cnxn:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": _("Connection Test Successful!"),
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Error !\nCheck connection credentials !"),
                    "type": "warning",
                    "sticky": False,
                },
            }

    def fetch_header_filter(self):
        header = []
        cnxn = self.connect_sql_server()
        if cnxn:
            cursor = cnxn.cursor()
            try:
                cursor.execute(self.query)
                head = [column[0] for column in cursor.description]
                if head:
                    for h in head:
                        idx = head.index(h)
                        header.append((str(idx), h))
            except Exception as e:
                raise UserError(_("Error on Query \n%s" % (e)))
        return header

    def fetch_data_from_sql(self, col=False, query=None, reconnect_attempts=2):
        """Fetches data from SQL Server and ensures results are lists."""

        query = query or self.query
        attempt = 0

        while attempt < reconnect_attempts:
            cnxn = self.connect_sql_server()
            if not cnxn:
                attempt += 1
                _logger.warning(
                    f"SQL connection failed. Retrying {attempt}/{reconnect_attempts}..."
                )
                continue

            cursor = cnxn.cursor()
            try:
                cursor.execute(query)
                raw_data = cursor.fetchall()  # Returns pyodbc.Row
                data = {
                    "datas": [list(row) for row in raw_data]
                }  # Convert rows to lists

                if col:
                    data["column"] = [column[0] for column in cursor.description]

                return data

            except pyodbc.Error as e:
                _logger.error(f"SQL Query Error in {self.name}: {e}")
                attempt += 1
            finally:
                cnxn.close()

        _logger.error(f"Failed to execute query after {reconnect_attempts} attempts.")
        return {}


class SqlIntegrationField(models.Model):
    _name = "sql.integration.line"
    _description = "SQL Integration Fields"
    _rec_name = "integration_id"

    integration_id = fields.Many2one(
        "sql.integration", "Integration ID", required=True, ondelete="cascade"
    )
    res_field_id = fields.Many2one(
        "ir.model.fields", string="Field", required=True, ondelete="cascade"
    )
    ttype = fields.Selection(related="res_field_id.ttype", string="Field Type")

    model_name = fields.Char(
        string="Model Name", compute="_compute_model_name", store=True
    )

    related_model = fields.Many2one(
        "ir.model",
        string="Related Model",
        compute="_compute_related_model",
        store=True,
    )

    evaluation_type = fields.Selection(
        [("seq", "Sequence"), ("value", "Value"), ("find", "Find Record")],
        "Evaluation Type",
        default="seq",
        required=True,
    )
    value_domain = fields.Char("Domain Filter")
    value = fields.Char("Value", required=True, compute="_compute_value", store=True)
    exclude = fields.Selection(
        [("create", "Create"), ("update", "Update")], "Exclude on"
    )
    make_readonly = fields.Boolean(
        "Readonly", compute="_compute_readonly_and_evaluation", store=True
    )

    @api.depends("integration_id.model_name")
    def _compute_model_name(self):
        """Ensures model_name is set correctly from integration_id.model_name"""
        for rec in self:
            rec.model_name = rec.integration_id.model_name or ""

    @api.depends("res_field_id")
    def _compute_related_model(self):
        """Computes related model based on res_field_id.relation."""
        for record in self:
            model_name = record.res_field_id.relation
            record.related_model = (
                self.env["ir.model"]
                .sudo()
                .search([("model", "=", model_name)], limit=1)
                if model_name
                else False
            )

    @api.depends("evaluation_type", "value_domain")
    def _compute_value(self):
        """Ensures value is correctly set when using 'find' evaluation type, without overwriting user input."""
        for rec in self:
            if rec.evaluation_type == "find" and rec.value_domain and not rec.value:
                rec.value = rec.value_domain

    @api.depends("res_field_id")
    def _compute_readonly_and_evaluation(self):
        """Automatically sets readonly and evaluation type based on field type."""
        for rec in self:
            if rec.ttype in {
                "many2one_reference",
                "many2one",
                "reference",
                "many2many",
                "one2many",
            }:
                rec.make_readonly = True
                if not rec.evaluation_type or rec.evaluation_type not in ["find"]:
                    rec.evaluation_type = "find"
            elif rec.ttype == "binary":
                rec.make_readonly = True
                if not rec.evaluation_type or rec.evaluation_type != "seq":
                    rec.evaluation_type = "seq"
            else:
                rec.make_readonly = False
