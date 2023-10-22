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
    _inherit = "res.partner"
    # _inherit = ["multi.company.abstract", "res.partner"]
    
    # channel_ids = fields.Many2many(
    #     'your.other.model',  
    #     relation='unique_relation_table_name', 
    #     column1='partner_id',
    #     column2='other_model_id',
    #     string='Channels'
    # )

    prescription_order_lines = fields.One2many('pod.prescription.order.line', 'prescription_order_id', 'Prescription Line')
    prescription_order_count = fields.Integer(string='Prescription Count', compute='_compute_prescription_order_count')
    prescription_order_ids = fields.One2many(
        "pod.prescription.order",
        "partner_id",
        string="Prescriptions",
        domain=[("active", "=", True)],
    )
    
    practice_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_company','=',True)], 
        string="Practice"
        )
    
    practitioner_id = fields.Many2one(
        'res.partner', 
        required=True, 
        index=True, 
        domain=[('is_practitioner','=',True)], 
        string="Practitioner"
        )
    
    patient_id = fields.Many2one(
        "pod.patient", 
        string="Patient",
        required=True, 
        index=True, 
        states={"draft": [("readonly", False)], "done": [("readonly", True)]}
    )

    @api.depends('prescription_order_ids')
    def _compute_prescription_order_count(self):
        for partner in self:
            partner.prescription_order_count = len(partner.prescription_order_ids)

    def action_view_prescription_orders(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'view_mode': 'kanban,tree,form',
            'res_model': 'pod.prescription.order',
            'domain': [('id', 'in', self.prescription_order_ids.ids)],  
            'context': {'default_partner_id': self.id},
        }
        return action