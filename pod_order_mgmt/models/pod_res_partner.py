# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from datetime import timedelta
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

class Partner(models.Model):
    _inherit = ["multi.company.abstract", "res.partner"]
    _name = 'res.partner'

    prescription_order_lines = fields.One2many('pod.prescription.order.line', 'prescription_order_id', 'Prescription Line')

    prescription_order_ids = fields.One2many(
        "pod.prescription.order",
        "practice_id",
        string="Practice Prescriptions",
        domain=[("active", "=", True)],
    )
    
    # prescription_count = fields.Integer(compute='get_prescription_count')

    # def open_partner_prescriptions(self):
    #     for records in self:
    #         return {
    #             'name':_('Prescriptions'),
    #             'view_type': 'form',
    #             'domain': [('partner_id', '=',records.id)],
    #             'res_model': 'pod.prescription.order',
    #             'view_id': False,
    #             'view_mode':'tree,form',
    #             'context':{'default_partner_id':self.id},
    #             'type': 'ir.actions.act_window',
    #         }

    # def get_prescription_count(self):
    #     for records in self:
    #         count = self.env['pod.prescription.order'].search_count([('partner_id','=',records.id)])
    #         records.prescription_count = count
    


