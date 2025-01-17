# -*- coding: utf-8 -*-

import base64
import csv

from io import StringIO
from odoo import models, fields, _
from odoo.exceptions import UserError


class SqlToCsv(models.TransientModel):
    _name = 'sql.to.csv'

    sql = fields.Text()
    csv_file = fields.Binary(string="CSV File")
    csv_filename = fields.Char()

    def get_str_data(self, item):
        return str(item) if item else ''

    def do_sql_to_csv(self):
        if ('update ' in self.sql.lower() and ' set ' in self.sql.lower()) or \
            'delete from' in self.sql.lower():
            raise UserError(_('You can only SELECT in SQL. Not UPDATE nor DELETE.'))
        try:
            self.env.cr.execute(self.sql)
            data = self.env.cr.dictfetchall()
            header = data[0].keys()
            f = StringIO()
            writer = csv.writer(f, delimiter=';', quotechar='"')
            writer.writerow(header)
            for row in data:
                writer.writerow([self.get_str_data(s) for s in row.values()])
            self.csv_file = base64.encodebytes(f.getvalue().encode('utf-8'))
            self.csv_filename = 'export_sql_%s.csv' % fields.Date.today().strftime('%Y_%m_%d_%H_%M')
        except:
            raise UserError(_('Error executing SQL: %s') % self.sql)
        return {
            'type': 'ir.actions.act_window',
            'name': 'SQL to CSV',
            'view_mode': 'form',
            'res_model': 'sql.to.csv',
            'res_id': self.id,
            'target': 'new',
        }
        
