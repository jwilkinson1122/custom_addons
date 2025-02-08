# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################
from odoo import api, fields, models, _
import pyodbc
from odoo.exceptions import UserError
import logging
from dateutil.relativedelta import relativedelta
import re
import base64

_logger = logging.getLogger(__name__)

ACCEPTED_FIELDS = ['many2many', 'one2many','many2one_reference', 'datetime', 'monetary', 'html', 'date', 'selection', 'many2one', 'float', 'reference', 'boolean', 'char', 'text', 'integer', 'binary']
# NOT_ACCEPTED = ['json', 'properties_definition', 'properties']


class SqlIntegration(models.Model):
    _name = 'sql.integration'
    _description = 'SQL Integration'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    server = fields.Char('Server', required=True)
    database = fields.Char('Database', required=True)
    sql_user = fields.Char('SQL User', required=True)
    sql_user_password = fields.Char('SQL User Password', required=True)
    query = fields.Text('Query')
    res_model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade')
    model_name = fields.Char(related='res_model_id.model', string='Model Name', readonly=True, store=True)
    filter_domain = fields.Char('Filter Domain',)# default='[("field_name","=", data[0])]')
    query_result = fields.Html('Query Result', copy=False)
    action_type = fields.Selection([('create', 'Create'),('create_not_exist', 'Create if not exist'),('update', 'Update'),('update_create_not_exist', 'Update & Create if not exist')], string="Action Type", default="create")
    integration_fields = fields.One2many('sql.integration.line', 'integration_id', string='Mappings', required=True)
    ready = fields.Boolean('Ready for integration', copy=False)
    enable_automation = fields.Boolean('Enable')
    next_call = fields.Datetime(string='Next Schedule')
    last_call = fields.Datetime(string='Last executed on')
    interval_number = fields.Integer('Execute Every', default=1)
    interval_unit = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'),
         ('years', 'Years')],
        string='Unit', default='days')

    def cron_auto_execution(self):
        now = fields.Datetime.now()
        records = self.env['sql.integration'].search([('enable_automation', '=', True),('next_call', '<=', now)])
        if records:
            for rec in records:
                rec.run_now()
                rec.next_call = rec.next_call + relativedelta(**{rec.interval_unit: rec.interval_number})

    def make_it_ready(self):
        if not self.res_model_id:
            raise UserError(_("Please choose Model !"))
        if not self.action_type:
            raise UserError(_("Please select Action Type !"))
        cnxn = self.connect_sql_server()
        if not cnxn:
            raise UserError(_("Error on connection with SQL !"))
        self.run_query()
        if not self.integration_fields:
            raise UserError(_("Please Mapp fields to integrate data !"))
        self.write({'ready': True})

    @api.onchange('query')
    def _onchange_query(self):
        for i in self:
            i.query_result = False
            i.ready = False

    @api.onchange('enable_automation')
    def _onchange_enable_automation(self):
        for i in self:
            if i.enable_automation:
                i.write({
                    'next_call': fields.Datetime.now()
                })

    def run_query(self):
        if self.query[:6].upper() == 'SELECT':
            query = 'SELECT TOP 3 * from (' + self.query + ')e'
            data = self.fetch_data_from_sql(col=True, query=query)
            html = '<table style="width:100%;overflow:scroll;"><tr>'
            for idx, col in enumerate(data['column']):
                html += f'<th style="border:1px solid black;padding:5px;background-color:#999999;color:#ffffff">[{idx}] {col}</th>'
            html += '</tr>'
            col_count = len(data['column'])
            for d in data['datas']:
                html += '<tr>'
                for count in range(col_count):
                    html += f'<td style="border:1px solid black;padding:3px;padding-left:5px;padding-right:5px;">{d[count]}</td>'
                html += '</tr>'
            html += '</table>'
            self.query_result = html
        else:
            self.query_result = False
            raise UserError('Wrong Query !!!\nQuery should start with "SELECT" !')

    def _get_unique_record(self, domain_filter):
        return self.env[self.model_name].search(domain_filter, limit=1)

    def _get_val_string(self, method, data=None):
        def remove_quotes(match):
            return match.group(0).replace('"', '')
        non_values = ['', 'NULL', 'null', 'False', 'FALSE']
        val_string = '{'
        for i in self.integration_fields:
            if method != i.exclude:
                if i.res_field_id.ttype in ['date', 'datetime']:
                    val_string += f"'{i.res_field_id.name}':"
                    if data[int(i.value)] in non_values:
                        val_string += 'False,'
                    else:
                        if i.evaluation_type == 'seq':
                            val_string += f"data[{i.value}],"
                        elif i.evaluation_type == 'value':
                            val_string += f"{i.value},"
                elif i.evaluation_type in ['seq', 'value']:
                    val_string += f"'{i.res_field_id.name}':"
                    if i.res_field_id.ttype in ['binary'] and i.evaluation_type == 'seq':
                        val_string += str(base64.b64encode(data[int(i.value)]))
                    else:
                        if i.evaluation_type == 'seq':
                            val_string += f"data[{i.value}],"
                        elif i.evaluation_type == 'value':
                            val_string += f"'{i.value}',"
                else:
                    pattern = r'"data\[\d+\]"'
                    domain = eval(re.sub(pattern, remove_quotes, i.value))
                    res = self.env[i.res_field_id.relation].search(domain, limit=1)
                    if res:
                        val_string += f"'{i.res_field_id.name}':"
                        if i.res_field_id.ttype in ['many2many', 'one2many']:
                            val_string += f"{res.ids},"
                        elif i.res_field_id.ttype in ['many2one', 'many2one_reference', 'reference']:
                            val_string += f"{res.id},"
                    else:
                        continue
        val_string += '}'
        return val_string

    def run_now(self):
        def remove_quotes(match):
            return match.group(0).replace('"', '')

        datas = self.fetch_data_from_sql()
        if datas:
            for data in datas['datas']:
                try:
                    with self.env.cr.savepoint():
                        if self.action_type == 'create':
                            vals = eval(self._get_val_string(method='create', data=data))
                            self.env[self.model_name].create(vals)
                        else:
                            pattern = r'"data\[\d+\]"'
                            domain = eval(re.sub(pattern, remove_quotes, self.filter_domain))
                            unique = self._get_unique_record(domain_filter=domain)
                            if self.action_type == 'create_not_exist':
                                vals = eval(self._get_val_string(method='create', data=data))
                                if not unique:
                                    self.env[self.model_name].create(vals)
                            elif self.action_type == 'update':
                                vals = eval(self._get_val_string(method='update', data=data))
                                if unique:
                                    unique.write(vals)
                            elif self.action_type == 'update_create_not_exist':
                                if unique:
                                    vals = eval(self._get_val_string(method='update', data=data))
                                    unique.write(vals)
                                else:
                                    vals = eval(self._get_val_string(method='create', data=data))
                                    self.env[self.model_name].create(vals)
                except Exception as e:
                    # raise UserError(_(f"Error: {e} for {data}"))
                    _logger.warning("Exception for MSSQL Integration %s from %s:", e, self.name)
            self.write({'last_call': fields.Datetime.now()})

    def connect_sql_server(self):
        sql = 'DRIVER={ODBC Driver 17 for SQL Server};  \
              SERVER=' + self.server + '; \
              DATABASE=' + self.database + ';\
              UID=' + self.sql_user + ';\
              PWD=' + self.sql_user_password + ';\
              Trusted_Connection=no;'
        try:
            cnxn = pyodbc.connect(sql)
            return cnxn
        except Exception as e:
            _logger.warning("Exception for connect_sql_server() %s from %s:", e, self.name)

    def test_sql_connection(self):
        cnxn = self.connect_sql_server()
        if cnxn:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Connection Test Successful!"),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Error !\nCheck connection credentials !'),
                    'type': 'warning',
                    'sticky': False,
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

    def fetch_data_from_sql(self, col=False, query=False):
        if not query:
            query = self.query
        cnxn = self.connect_sql_server()
        if cnxn:
            cursor = cnxn.cursor()
            try:
                cursor.execute(query)
                data = {}
                if col:
                    data['column'] = [column[0] for column in cursor.description]
                data['datas'] = cursor.fetchall()
                return data
            except Exception as e:
                raise UserError(_("Error on Query \n%s" % (e)))


class SqlIntegrationField(models.Model):
    _name = 'sql.integration.line'
    _description = 'SQL Integration Fields'
    _rec_name = 'integration_id'

    # def _get_value_selection(self):
    #     return self.integration_id.fetch_header_filter()

    integration_id = fields.Many2one('sql.integration', 'Integration ID', required=True, ondelete='cascade')
    res_field_id = fields.Many2one('ir.model.fields', string='Field', required=True, ondelete='cascade')
    ttype = fields.Selection(related='res_field_id.ttype', string='Field Type')
    model_name = fields.Char(related='res_field_id.relation', string='Model Name')
    evaluation_type = fields.Selection([('seq', 'Sequence'), ('value', 'Value'), ('find', 'Find Record')], 'Evaluation Type', default='seq', required=True)
    value_domain = fields.Char('Domain Filter')
    value = fields.Char('Value', required=True)
    exclude = fields.Selection([('create', 'Create'), ('update', 'Update')], 'Exclude on')
    make_readonly = fields.Boolean('Readonly')

    @api.onchange('value_domain')
    def _onchange_value_domain(self):
        for rec in self:
            if rec.evaluation_type == 'find' and rec.value_domain:
                rec.value = rec.value_domain

    @api.onchange('res_field_id')
    def _onchange_res_field_id(self):
        for i in self:
            if i.ttype in ['many2one_reference', 'many2one', 'reference', 'many2many', 'one2many']:
                i.write({'make_readonly': True, 'evaluation_type': 'find'})
            elif i.ttype in ['binary']:
                i.write({'make_readonly': True, 'evaluation_type': 'seq'})
            else:
                i.write({'make_readonly': False, 'evaluation_type': 'seq'})