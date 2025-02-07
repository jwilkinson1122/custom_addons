# -*- coding: utf-8 -*-
import re
import ast
import base64
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

    def cron_auto_execution(self):
        """Automated execution of integrations based on scheduling."""
        now = fields.Datetime.now()
        records = self.search(
            [("enable_automation", "=", True), ("next_call", "<=", now)]
        )
        for rec in records:
            rec.run_now()
            rec.next_call += relativedelta(**{rec.interval_unit: rec.interval_number})

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

    def _get_val_dict(self, method, data):
        """
        Constructs a dictionary of values for integration fields, handling different field types.
        """
        non_values = {"", "NULL", "null", "False", "FALSE"}
        val_dict = {}

        for field in self.integration_fields:
            if method == field.exclude:
                continue  # Skip excluded fields

            field_name = field.res_field_id.name
            field_type = field.res_field_id.ttype
            field_value = field.value

            # Handle evaluation types
            if field.evaluation_type == "seq":
                val = (
                    None
                    if data[int(field_value)] in non_values
                    else data[int(field_value)]
                )
            elif field.evaluation_type == "value":
                val = field_value
            elif field.evaluation_type == "find":
                val = self._resolve_related_value(field, data)
            else:
                continue  # Unknown evaluation type, skip field

            # Process specific field types
            if field_type in ["date", "datetime"]:
                val_dict[field_name] = False if val in non_values else val
            elif field_type == "binary" and field.evaluation_type == "seq":
                val_dict[field_name] = (
                    base64.b64encode(data[int(field_value)]).decode()
                    if field_value.isdigit()
                    else None
                )
            else:
                val_dict[field_name] = val

        return val_dict

    # def _resolve_related_value(self, field, data):
    #     """
    #     Resolves 'find' evaluation type by searching for a related record.
    #     """
    #     try:
    #         pattern = r"data\[(\d+)\]"
    #         safe_value = re.sub(
    #             pattern, lambda m: f'"{data[int(m.group(1))]}"', field.value
    #         )
    #         domain = ast.literal_eval(safe_value)

    #         res = self.env[field.res_field_id.relation].search(domain, limit=1)
    #         if res:
    #             if field.res_field_id.ttype in [
    #                 "many2one",
    #                 "many2one_reference",
    #                 "reference",
    #             ]:
    #                 return res.id
    #             elif field.res_field_id.ttype in ["many2many", "one2many"]:
    #                 return res.ids
    #     except Exception as e:
    #         _logger.warning(
    #             f"Error evaluating domain for field {field.res_field_id.name}: {e}"
    #         )
    #     return None

    def _resolve_related_value(self, field, data):
        # print('_resolve_related_value: ', _resolve_related_value)
        """
        Resolves 'find' evaluation type by searching for a related record.
        Properly replaces "data[N]" placeholders with actual values.
        """
        try:
            # Log the raw domain value before replacement
            _logger.info(
                f"Raw domain string for {field.res_field_id.name}: {field.value}"
            )

            # Replace data[N] occurrences safely
            pattern = r"data\[(\d+)\]"
            safe_value = re.sub(
                pattern, lambda m: f'"{data[int(m.group(1))]}"', field.value
            )

            # Log the domain after replacement
            _logger.info(
                f"Transformed domain string for {field.res_field_id.name}: {safe_value}"
            )

            # Evaluate the corrected domain
            domain = ast.literal_eval(safe_value)

            # Log the final evaluated domain
            _logger.info(f"Evaluated domain for {field.res_field_id.name}: {domain}")

            # Perform the search
            res = self.env[field.res_field_id.relation].search(domain, limit=1)
            if res:
                _logger.info(f"Record found: {res.id if res.id else res.ids}")

                if field.res_field_id.ttype in [
                    "many2one",
                    "many2one_reference",
                    "reference",
                ]:
                    return res.id
                elif field.res_field_id.ttype in ["many2many", "one2many"]:
                    return res.ids
        except Exception as e:
            _logger.error(f"Error evaluating domain for {field.res_field_id.name}: {e}")

        return None

    # name = "John"
    # age = 30
    # print("Name:", name)
    # print("Age:", age)

    # print("_resolve_related_value: ", _resolve_related_value)
    # print("DEBUG: Checking domain replacement:", _resolve_related_value(field, data))

    # def _resolve_related_value(self, field, data):
    #     """
    #     Resolves 'find' evaluation type by searching for a related record.
    #     Properly replaces "data[N]" placeholders with actual values.
    #     """
    #     try:
    #         pattern = r"data\[(\d+)\]"
    #         safe_value = re.sub(pattern, lambda m: f'"{data[int(m.group(1))]}"', field.value)
    #         domain = ast.literal_eval(safe_value)
    #         res = self.env[field.res_field_id.relation].search(domain, limit=1)
    #         if res:
    #             if field.res_field_id.ttype in ["many2one", "many2one_reference", "reference"]:
    #                 return res.id
    #             elif field.res_field_id.ttype in ["many2many", "one2many"]:
    #                 return res.ids
    #     except Exception as e:
    #         _logger.warning(f"Error evaluating domain for field {field.res_field_id.name}: {e}")

    #     return None

    def run_now(self):
        """Executes the integration process."""
        self.ensure_one()
        datas = self.fetch_data_from_sql()
        if not datas:
            return

        for data in datas["datas"]:
            try:
                with self.env.cr.savepoint():
                    vals = self._get_val_dict(
                        "create" if self.action_type.startswith("create") else "update",
                        data,
                    )
                    domain = ast.literal_eval(
                        re.sub(
                            r'"data\[\d+\]"',
                            lambda m: m.group(0).replace('"', ""),
                            self.filter_domain,
                        )
                    )
                    unique = self._get_unique_record(domain)

                    if self.action_type == "create" or (
                        self.action_type == "create_not_exist" and not unique
                    ):
                        self.env[self.model_name].create(vals)
                    elif self.action_type == "update" and unique:
                        unique.write(vals)
                    elif self.action_type == "update_create_not_exist":
                        (
                            unique.write(vals)
                            if unique
                            else self.env[self.model_name].create(vals)
                        )
            except Exception as e:
                _logger.warning("Exception in SQL Integration %s: %s", self.name, e)

        self.last_call = fields.Datetime.now()

    def connect_sql_server(self):
        """Establishes a connection to SQL Server."""
        try:
            return pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};"
                f"DATABASE={self.database};UID={self.sql_user};PWD={self.sql_user_password};Trusted_Connection=no;"
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

    def fetch_data_from_sql(self, col=False, query=None):
        """Fetches data from SQL Server."""
        cnxn = self.connect_sql_server()
        if not cnxn:
            return {}

        query = query or self.query
        cursor = cnxn.cursor()
        try:
            cursor.execute(query)
            data = {"datas": cursor.fetchall()}
            if col:
                data["column"] = [column[0] for column in cursor.description]
            return data
        except Exception as e:
            _logger.error("SQL Query Error in %s: %s", self.name, e)
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

    # @api.depends("res_field_id")
    # def _compute_field_properties(self):
    #     for rec in self:
    #         if rec.res_field_id.ttype in [
    #             "many2one_reference",
    #             "many2one",
    #             "reference",
    #             "many2many",
    #             "one2many",
    #         ]:
    #             rec.make_readonly = True
    #             rec.evaluation_type = "find"
    #         elif rec.res_field_id.ttype == "binary":
    #             rec.make_readonly = True
    #             rec.evaluation_type = "seq"
    #         else:
    #             rec.make_readonly = False
    #             rec.evaluation_type = "seq"


# ACCEPTED_FIELDS = [
#     "many2many",
#     "one2many",
#     "many2one_reference",
#     "datetime",
#     "monetary",
#     "html",
#     "date",
#     "selection",
#     "many2one",
#     "float",
#     "reference",
#     "boolean",
#     "char",
#     "text",
#     "integer",
#     "binary",
# ]
# NOT_ACCEPTED = ['json', 'properties_definition', 'properties']


# class SqlIntegration(models.Model):
#     _name = "sql.integration"
#     _description = "SQL Integration"

#     name = fields.Char("Name", required=True)
#     active = fields.Boolean("Active", default=True)
#     server = fields.Char("Server", required=True)
#     database = fields.Char("Database", required=True)
#     sql_user = fields.Char("SQL User", required=True)
#     sql_user_password = fields.Char("SQL User Password", required=True)
#     query = fields.Text("Query")
#     res_model_id = fields.Many2one("ir.model", string="Model", ondelete="cascade")
#     model_name = fields.Char(
# related="res_model_id.model", string="Model Name", readonly=True, store=True
#     )
#     filter_domain = fields.Char(
#         "Filter Domain",
#     )
#     query_result = fields.Html("Query Result", copy=False)
#     action_type = fields.Selection(
#         [
#             ("create", "Create"),
#             ("create_not_exist", "Create if not exist"),
#             ("update", "Update"),
#             ("update_create_not_exist", "Update & Create if not exist"),
#         ],
# string="Action Type",
# default="create",
#     )
#     integration_fields = fields.One2many(
#         "sql.integration.line", "integration_id", string="Mappings", required=True
#     )
#     ready = fields.Boolean("Ready for integration", copy=False)
#     enable_automation = fields.Boolean("Enable")
#     next_call = fields.Datetime(string="Next Schedule")
#     last_call = fields.Datetime(string="Last executed on")
#     interval_number = fields.Integer("Execute Every", default=1)
#     interval_unit = fields.Selection(
#         [
#             ("minutes", "Minutes"),
#             ("hours", "Hours"),
#             ("days", "Days"),
#             ("weeks", "Weeks"),
#             ("months", "Months"),
#             ("years", "Years"),
#         ],
# string="Unit",
# default="days",
#     )

#     def cron_auto_execution(self):
#         now = fields.Datetime.now()
#         records = self.env["sql.integration"].search(
#             [("enable_automation", "=", True), ("next_call", "<=", now)]
#         )
#         if records:
#             for rec in records:
#                 rec.run_now()
#                 rec.next_call = rec.next_call + relativedelta(
#                     **{rec.interval_unit: rec.interval_number}
#                 )

#     def make_it_ready(self):
#         if not self.res_model_id:
#             raise UserError(_("Please choose Model !"))
#         if not self.action_type:
#             raise UserError(_("Please select Action Type !"))
#         cnxn = self.connect_sql_server()
#         if not cnxn:
#             raise UserError(_("Error on connection with SQL !"))
#         self.run_query()
#         if not self.integration_fields:
#             raise UserError(_("Please Mapp fields to integrate data !"))
#         self.write({"ready": True})

#     @api.onchange("query")
#     def _onchange_query(self):
#         for i in self:
#             i.query_result = False
#             i.ready = False

#     @api.onchange("enable_automation")
#     def _onchange_enable_automation(self):
#         for i in self:
#             if i.enable_automation:
#                 i.write({"next_call": fields.Datetime.now()})

#     def run_query(self):
#         if self.query[:6].upper() == "SELECT":
#             query = "SELECT TOP 3 * from (" + self.query + ")e"
#             data = self.fetch_data_from_sql(col=True, query=query)
#             html = '<table style="width:100%;overflow:scroll;"><tr>'
#             for idx, col in enumerate(data["column"]):
#                 html += f'<th style="border:1px solid black;padding:5px;background-color:#999999;color:#ffffff">[{idx}] {col}</th>'
#             html += "</tr>"
#             col_count = len(data["column"])
#             for d in data["datas"]:
#                 html += "<tr>"
#                 for count in range(col_count):
#                     html += f'<td style="border:1px solid black;padding:3px;padding-left:5px;padding-right:5px;">{d[count]}</td>'
#                 html += "</tr>"
#             html += "</table>"
#             self.query_result = html
#         else:
#             self.query_result = False
#             raise UserError('Wrong Query !!!\nQuery should start with "SELECT" !')

#     def _get_unique_record(self, domain_filter):
#         return self.env[self.model_name].search(domain_filter, limit=1)

#     def _get_val_string(self, method, data=None):
#         def remove_quotes(match):
#             return match.group(0).replace('"', "")

#         non_values = ["", "NULL", "null", "False", "FALSE"]
#         val_string = "{"
#         for i in self.integration_fields:
#             if method != i.exclude:
#                 if i.res_field_id.ttype in ["date", "datetime"]:
#                     val_string += f"'{i.res_field_id.name}':"
#                     if data[int(i.value)] in non_values:
#                         val_string += "False,"
#                     else:
#                         if i.evaluation_type == "seq":
#                             val_string += f"data[{i.value}],"
#                         elif i.evaluation_type == "value":
#                             val_string += f"{i.value},"
#                 elif i.evaluation_type in ["seq", "value"]:
#                     val_string += f"'{i.res_field_id.name}':"
#                     if (
#                         i.res_field_id.ttype in ["binary"]
#                         and i.evaluation_type == "seq"
#                     ):
#                         val_string += str(base64.b64encode(data[int(i.value)]))
#                     else:
#                         if i.evaluation_type == "seq":
#                             val_string += f"data[{i.value}],"
#                         elif i.evaluation_type == "value":
#                             val_string += f"'{i.value}',"
#                 else:
#                     pattern = r'"data\[\d+\]"'
#                     domain = eval(re.sub(pattern, remove_quotes, i.value))
#                     res = self.env[i.res_field_id.relation].search(domain, limit=1)
#                     if res:
#                         val_string += f"'{i.res_field_id.name}':"
#                         if i.res_field_id.ttype in ["many2many", "one2many"]:
#                             val_string += f"{res.ids},"
#                         elif i.res_field_id.ttype in [
#                             "many2one",
#                             "many2one_reference",
#                             "reference",
#                         ]:
#                             val_string += f"{res.id},"
#                     else:
#                         continue
#         val_string += "}"
#         return val_string

#     def run_now(self):
#         def remove_quotes(match):
#             return match.group(0).replace('"', "")

#         datas = self.fetch_data_from_sql()
#         if datas:
#             for data in datas["datas"]:
#                 try:
#                     with self.env.cr.savepoint():
#                         if self.action_type == "create":
#                             vals = eval(
# self._get_val_string(method="create", data=data)
#                             )
#                             self.env[self.model_name].create(vals)
#                         else:
#                             pattern = r'"data\[\d+\]"'
#                             domain = eval(
#                                 re.sub(pattern, remove_quotes, self.filter_domain)
#                             )
#                             unique = self._get_unique_record(domain_filter=domain)
#                             if self.action_type == "create_not_exist":
#                                 vals = eval(
# self._get_val_string(method="create", data=data)
#                                 )
#                                 if not unique:
#                                     self.env[self.model_name].create(vals)
#                             elif self.action_type == "update":
#                                 vals = eval(
# self._get_val_string(method="update", data=data)
#                                 )
#                                 if unique:
#                                     unique.write(vals)
#                             elif self.action_type == "update_create_not_exist":
#                                 if unique:
#                                     vals = eval(
# self._get_val_string(method="update", data=data)
#                                     )
#                                     unique.write(vals)
#                                 else:
#                                     vals = eval(
# self._get_val_string(method="create", data=data)
#                                     )
#                                     self.env[self.model_name].create(vals)
#                 except Exception as e:
#                     _logger.warning(
#                         "Exception for MSSQL Integration %s from %s:", e, self.name
#                     )
#             self.write({"last_call": fields.Datetime.now()})

#     def connect_sql_server(self):
#         sql = (
#             "DRIVER={ODBC Driver 17 for SQL Server};  \
# SERVER="
#             + self.server
#             + "; \
# DATABASE="
#             + self.database
#             + ";\
# UID="
#             + self.sql_user
#             + ";\
# PWD="
#             + self.sql_user_password
#             + ";\
# Trusted_Connection=no;"
#         )
#         try:
#             cnxn = pyodbc.connect(sql)
#             return cnxn
#         except Exception as e:
#             _logger.warning(
#                 "Exception for connect_sql_server() %s from %s:", e, self.name
#             )

#     def test_sql_connection(self):
#         cnxn = self.connect_sql_server()
#         if cnxn:
#             return {
#                 "type": "ir.actions.client",
#                 "tag": "display_notification",
#                 "params": {
#                     "message": _("Connection Test Successful!"),
#                     "type": "success",
#                     "sticky": False,
#                 },
#             }
#         else:
#             return {
#                 "type": "ir.actions.client",
#                 "tag": "display_notification",
#                 "params": {
#                     "title": _("Connection Error !\nCheck connection credentials !"),
#                     "type": "warning",
#                     "sticky": False,
#                 },
#             }

#     def fetch_header_filter(self):
#         header = []
#         cnxn = self.connect_sql_server()
#         if cnxn:
#             cursor = cnxn.cursor()
#             try:
#                 cursor.execute(self.query)
#                 head = [column[0] for column in cursor.description]
#                 if head:
#                     for h in head:
#                         idx = head.index(h)
#                         header.append((str(idx), h))
#             except Exception as e:
#                 raise UserError(_("Error on Query \n%s" % (e)))
#         return header

#     def fetch_data_from_sql(self, col=False, query=False):
#         if not query:
#             query = self.query
#         cnxn = self.connect_sql_server()
#         if cnxn:
#             cursor = cnxn.cursor()
#             try:
#                 cursor.execute(query)
#                 data = {}
#                 if col:
#                     data["column"] = [column[0] for column in cursor.description]
#                 data["datas"] = cursor.fetchall()
#                 return data
#             except Exception as e:
#                 raise UserError(_("Error on Query \n%s" % (e)))


# class SqlIntegrationField(models.Model):
#     _name = "sql.integration.line"
#     _description = "SQL Integration Fields"
#     _rec_name = "integration_id"

#     integration_id = fields.Many2one(
#         "sql.integration", "Integration ID", required=True, ondelete="cascade"
#     )
#     res_field_id = fields.Many2one(
#         "ir.model.fields", string="Field", required=True, ondelete="cascade"
#     )
#     ttype = fields.Selection(related="res_field_id.ttype", string="Field Type")
#     model_name = fields.Char(related="res_field_id.relation", string="Model Name")
#     evaluation_type = fields.Selection(
#         [("seq", "Sequence"), ("value", "Value"), ("find", "Find Record")],
#         "Evaluation Type",
# default="seq",
# required=True,
#     )
#     value_domain = fields.Char("Domain Filter")
#     value = fields.Char("Value", required=True)
#     exclude = fields.Selection(
#         [("create", "Create"), ("update", "Update")], "Exclude on"
#     )
#     make_readonly = fields.Boolean("Readonly")

#     @api.onchange("value_domain")
#     def _onchange_value_domain(self):
#         for rec in self:
#             if rec.evaluation_type == "find" and rec.value_domain:
#                 rec.value = rec.value_domain

#     @api.onchange("res_field_id")
#     def _onchange_res_field_id(self):
#         for i in self:
#             if i.ttype in [
#                 "many2one_reference",
#                 "many2one",
#                 "reference",
#                 "many2many",
#                 "one2many",
#             ]:
#                 i.write({"make_readonly": True, "evaluation_type": "find"})
#             elif i.ttype in ["binary"]:
#                 i.write({"make_readonly": True, "evaluation_type": "seq"})
#             else:
#                 i.write({"make_readonly": False, "evaluation_type": "seq"})
